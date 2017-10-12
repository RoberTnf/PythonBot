"""Constants, SQL connectors"""

# Language support
BOT_USERNAME = "/u/InterpreterBot"
INPUT_FILE = "input"
LANGUAGES = {
    "python": {
        "command": ["python3", INPUT_FILE],
        "callsign": "python"
    }
}

# execution params
TEST = True
MAX_CALLS_PER_POST = 5 
MAX_TIME = 5
BLOCKED_USERS = []
ALLOWED_SUBREDDITS = [
    "testingground4bots", "python", "programming", "learnprogramming",
    "learnpython"]
MAX_LENGTH_ALLOWED = 1000

# firejail
FIREJAIL_COMMAND = ["firejail", "--profile=firejail.profile", "-c"]
FIREJAIL_DIR = "firejail_dir/"

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
