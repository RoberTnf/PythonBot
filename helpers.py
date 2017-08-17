"""
Contains helping function.
"""

import subprocess
import os
import os.path
import signal

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
            output_bytes = subprocess.check_output(self.command, stderr=subprocess.STDOUT)[64:]
            self.output = str(output_bytes)
        except subprocess.CalledProcessError as err:
            self.output = str(err.output[64:])

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
