"""Constants, SQL connectors"""

from os import environ

# Language support
BOT_USERNAME = "/u/InterpreterBot"
INPUT_FILE = "input"
LANGUAGES = {
    "python": {
        "command": ["py3-bot/bin/python", INPUT_FILE],
        "callsign": "python"
    }
}

# firejail
FIREJAIL_COMMAND = ["firejail", "--profile=firejail.profile", "-c"]
FIREJAIL_DIR = "firejail_dir/"

# execution params
TEST = False 
MAX_TIME = 5
ALLOWED_USERS = ["AgressiveYorkshire", "aphoenix"]
ALLOWED_SUBREDDITS = ["testingground4bots"]
MAX_LENGTH_ALLOWED = 1000

# Reddit params
NUMBER_OF_POSTS = 100
CALLSIGN = "/u/InterpreterBot python"

OUTPUT_TEMPLATE = """
{number}:

{output}
"""
SIGNATURE = """
***
^^I'm ^^a ^^bot, ^^check ^^me ^^out ^^at: ^^https://github.com/RoberTnf/PythonBot
"""
