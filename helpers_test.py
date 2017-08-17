"""
General tests for the bot
"""

import unittest
from helpers import Interpreter
import os
import os.path

class BotTests(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()

    def tearDown(self):
        self.interpreter.delete_input()

    def test_create_input(self):
        if os.path.exists(self.interpreter.input_file):
            self.interpreter.delete_input()

        self.interpreter.create_input()
        self.assertTrue(os.path.exists(self.interpreter.input_file))

    def test_delete_input(self):
        if not os.path.exists(self.interpreter.input_file):
            self.interpreter.create_input()

        self.interpreter.delete_input()
        self.assertFalse(os.path.exists(self.interpreter.input_file))

    def test_hello_world(self):
        self.interpreter.run("print('Hello, World!')")
        self.assertEqual(self.interpreter.output,
                         "Hello, World!\n")

    def test_tildes(self):
        self.interpreter.run("print('Hola Martín!')")
        self.assertEqual(self.interpreter.output,
                         "Hola Martín!\n")

    def test_errors(self):
        error_str = """Traceback (most recent call last):
  File "input.py", line 1, in <module>
    asdkmoasf
NameError: name 'asdkmoasf' is not defined
"""
        self.interpreter.run("asdkmoasf")
        self.assertEqual(error_str, self.interpreter.output)

if __name__ == "__main__":
    unittest.main()
