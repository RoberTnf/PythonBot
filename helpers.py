"""
Contains helping function.
"""

import subprocess
import re
import html.entities
import config
import shutil
import os

# https://stackoverflow.com/questions/25027122/break-the-function-after-certain-time

class TimeoutException(Exception):
    """Custom exception class"""
    pass

def timeout_handler(signum, frame):
    """# Custom signal handler"""
    raise TimeoutException

class Interpreter(object):

    """
    Class to securely run code fed to us.
    """

    def __init__(self, language):

        self.firejail_dir = config.FIREJAIL_DIR
        self.input_file = self.firejail_dir + config.INPUT_FILE
        self.command = config.FIREJAIL_COMMAND + language["command"]
        self.output = ""

    def run(self, code):
        """
        Runs code and returns the output
        """
        self.create_input(code)

        try:
            output_bytes = subprocess.check_output(self.command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            output_bytes = err.output

        output_bytes = output_bytes[output_bytes.find(b'\n'):]
        output = str(output_bytes, "utf-8")
        # if you take off, everything breaks, even if it makes no sense
        # if you print output, it gives you what you expect
        # however, if you, in a terminal, evaluate output, the string is different
        # I don't know why this happens
        self.output = (output[output.find("\x070")+2:]+".")[-1]
        clean_up()

    def create_input(self, code=""):
        """
        Creates temporary file and fills it with the code to be executed
        """

        with open(self.input_file, "w+") as tmp_file:
            tmp_file.write(code)


def clean_up():
    """
    Kills every firejailed process, cleans firejail_dir folder
    """

    command = ["firejail", "--list"]
    kill = ["kill", "-9"]
    pids = [int(s[:s.find(":")]) for s in str(subprocess.check_output(command), "utf-8")\
        .split("\n")[:-1]]
    for pid in pids:
        # os.kill sometimes doesn't work
        # os.kill(PID, signal.SIGTERM)
        try:
            subprocess.check_call(kill + [str(pid)])
        except subprocess.CalledProcessError:
            pass
    # delete everything in firejail_dir
    for the_file in os.listdir(config.FIREJAIL_DIR):
        file_path = os.path.join(config.FIREJAIL_DIR, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
def unescape(text):
    """
    Removes HTML or XML character references and entities from a text string.
    @param text The HTML (or XML) source text.
    @return The plain text, as a Unicode string, if necessary."""
    def fixup(match):
        """Auxiliary function"""
        text = match.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return chr(int(text[3:-1], 16))
                return chr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = chr(html.entities.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub(r"&#?\w+;", fixup, text)
