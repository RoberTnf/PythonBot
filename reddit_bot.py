#!/usr/bin/env python

"""
Reddit bot runner.
"""

import signal
import praw
import praw.models
from helpers import Interpreter, timeout_handler, TimeoutException, unescape
import config


# https://stackoverflow.com/questions/25027122/break-the-function-after-certain-time
# Change the behavior of SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)

class BotRunner(object):
    """
    Class for the bot object, handles everything related to reddit and praw.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, bot, language):
        self.bot = bot
        self.interpreter = Interpreter(language)
        self.language = language["callsign"]
        self.callsign = config.BOT_USERNAME + " " + language["callsign"]
        self.new_comments = []
        self.outputs = []
        self.messages = []
        self.codes = []

    def get_new_comments(self):
        """
        Gets comment in which the bot is mentioned using the unread messages in the inbox
        """

        comments = []
        for comment in self.bot.inbox.unread():
            if self.callsign.lower() in comment.body.lower() and comment.author\
                not in config.BLOCKED_USERS and comment.subreddit in config.ALLOWED_SUBREDDITS:
                comments.append(comment)

                print("{}: Summon from: {}".format(self.language, comment.permalink()))

        self.new_comments = comments

    def get_code_from_comments(self):
        """
        Extracts codes to be run from the comments
        """

        codes = []
        for comment in self.new_comments:
            line_list = comment.body.split("\n")
            line_number = 0
            codes.append([])
            number_of_calls = min(config.MAX_CALLS_PER_POST, line_list.count(self.callsign))
            # get starting lines for code
            for _ in range(number_of_calls):
                code = ""
                line_number = line_list.index(self.callsign, line_number)
                for line in line_list[line_number+1:]:
                    # if the comment block stops
                    if line.startswith("    ") or line == "":
                        code += "\n" + unescape(line[4:])
                        line_number += 1
                    else:
                        codes[-1].append(code)
                        break
            if len(codes[-1]) != line_list.count(number_of_calls):
                codes[-1].append(code)
        self.codes = codes

    def execute_codes(self):
        """
        Executes codes previously extracted and gets the output
        """

        for code in self.codes:
            self.outputs.append([])
            for sub_code in code:
                signal.alarm(config.MAX_TIME)
                try:
                    self.interpreter.run(sub_code)
                    self.outputs[-1].append(self.interpreter.output)
                except TimeoutException:
                    self.outputs[-1].append(
                        "You exceded the maximum time for interpreting your code.\n")
                    # self.interpreter.clear_files()
                else:
                    # reset alarm
                    signal.alarm(0)

    def get_messages_from_outputs(self):
        """
        Formats messages to be replied
        """

        messages = []
        for output in self.outputs:
            messages.append("")
            for i, sub_output in enumerate(output):
                sub_output = "    " + sub_output
                sub_output = sub_output.replace("\n", "\n    ")
                if len(sub_output) > config.MAX_LENGTH_ALLOWED:
                    sub_output = "    " + sub_output[len(sub_output)-config.MAX_LENGTH_ALLOWED:]
                    sub_output += "This message execeded the character limit"
                messages[-1] += config.OUTPUT_TEMPLATE.format(number=i+1, output=sub_output)
            messages[-1] += config.SIGNATURE

        self.messages = messages

    def reply(self):
        """
        Replies to every comment
        """
        for (comment, message) in zip(self.new_comments, self.messages):
            try:
                comment.reply(message)
                print("Replied.")
                comment.mark_read()
            except praw.exceptions.APIException as err:
                print(err)

    def clean_up(self):
        """
        Sets up for a new iteration of the main loop
        """

        self.new_comments = []
        self.outputs = []
        self.messages = []
        self.codes = []

    def run(self):
        """
        Does an iteration of the main loop, gets comments, executes code and replies
        """

        self.get_new_comments()
        self.get_code_from_comments()
        self.execute_codes()
        self.get_messages_from_outputs()


        if not config.TEST:
            self.reply()
        else:
            for message in self.messages:
                print(message)
        self.clean_up()

if __name__ == "__main__":
    print("Starting bot.")
    BOT = praw.Reddit('pythonBot')
    RUNNERS = []

    for LANGUAGE in config.LANGUAGES.values():
        RUNNERS.append(BotRunner(BOT, LANGUAGE))
    while True:
        try:
            for runner in RUNNERS:
                runner.run()
        except Exception as excep: # pylint: disable=W0703
            with open("log.txt", "a+") as f:
                print(str(excep))
                f.write(str(excep)+"\n")
