"""
Contains helping function.
"""

import subprocess
import os
import os.path
import signal
import re, html.entities

FIREJAIL_COMMAND = ["firejail", "--profile=firejail.profile", "-c", "python3"]
FIREJAIL_DIR = "firejail_dir/"
INPUT = "input.py"

ACCEPTED_FILES = ['./virtualenv/']


# https://stackoverflow.com/questions/25027122/break-the-function-after-certain-time

class TimeoutException(Exception):   # Custom exception class
    pass

def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException

class Interpreter(object):

    """
    Class to securely run code fed to us.
    """

    def __init__(self, firejail_command=FIREJAIL_COMMAND, input_file=INPUT,
                 firejail_dir=FIREJAIL_DIR):

        self.firejail_dir = firejail_dir
        self.input_file = firejail_dir + input_file
        self.command = firejail_command + [input_file]
        self.output = ""

    def run(self, code):
        """
        Runs code and returns the output
        """

        self.create_input(code)

        try:
            output_bytes = subprocess.check_output(self.command, stderr=subprocess.STDOUT)
            self.output = str(output_bytes, "utf-8")[64:]
        except subprocess.CalledProcessError as err:
            self.output = str(err.output, "utf-8")[64:]

        self.clean_up()

        self.delete_input()

    def create_input(self, code=""):
        """
        Creates temporary file and fills it with the code to be executed
        """

        with open(self.input_file, "w+") as tmp_file:
            tmp_file.write(code)


    def delete_input(self):
        """
        Deletes temporary file
        """

        if os.path.exists(self.input_file):
            os.remove(self.input_file)

    def clear_files(self):
        for root, dirs, files in os.walk(top=self.firejail_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def clean_up(self):
        command = ["firejail", "--list"]
        PIDS = [int(s[:5]) for s in str(subprocess.check_output(command), "utf-8").split("\n")[:-1]]
        for PID in PIDS:
            os.kill(PID, signal.SIGTERM)

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = chr(html.entities.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)
