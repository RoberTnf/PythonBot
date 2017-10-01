#!/usr/bin/env python

"""
Reddit bot runner.
"""
from datetime import datetime
import sqlite3
import praw
import praw.models
from helpers import Interpreter, timeout_handler, TimeoutException, unescape
import signal
import config


# https://stackoverflow.com/questions/25027122/break-the-function-after-certain-time
# Change the behavior of SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)

class BotRunner(object):

    def __init__(self, cursor, bot, conn, language, tablename="comments"):
        self.tablename = tablename
        self.cursor = cursor
        self.bot = bot
        self.language = language["callsign"]
        self.callsign = config.BOT_USERNAME + " " + language["callsign"]
        self.new_comments = []
        self.outputs = []
        self.interpreter = Interpreter(language)
        self.messages = []
        self.conn = conn
        self.codes = []

        cursor.execute(config.SQL_CREATE_TABLE_REDDIT.format(tablename=self.tablename))

    def get_new_comments(self):
        comments = []
        for c in self.bot.inbox.unread():
            if self.callsign.lower() in c.body.lower() and c.author in config.ALLOWED_USERS\
                and c.subreddit in config.ALLOWED_SUBREDDITS:
                comments.append(c)

                print("{}: Summon from: {}".format(self.language, c.permalink()))

        self.new_comments = comments

    def get_code_from_comments(self):

        codes = []
        for comment in self.new_comments:
            line_list = comment.body.split("\n")
            last_stop = 0
            codes.append([])
            # get starting lines for code
            for i in range(line_list.count(self.callsign)):
                code = ""
                for line in line_list[line_list.index(self.callsign, last_stop)+1:]:
                    # if the comment block stops
                    if line.startswith("    ") or line == "":
                        code += "\n" + unescape(line[4:])
                        last_stop += 1
                    else:
                        codes[-1].append(code)
                        break
            if len(codes[-1]) != line_list.count(self.callsign):
                codes[-1].append(code)
        self.codes = codes

    def execute_codes(self):
        for code in self.codes:
            self.outputs.append([])
            for sub_code in code:
                signal.alarm(config.MAX_TIME)
                try:
                    self.interpreter.run(sub_code)
                    self.outputs[-1].append(self.interpreter.output)
                except TimeoutException:
                    self.outputs[-1].append("You exceded the maximum time for interpreting your code.\n")
                    # self.interpreter.clear_files()
                else:
                    # reset alarm
                    signal.alarm(0)

    def get_messages_from_outputs(self):
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
        for (comment, message) in zip(self.new_comments, self.messages):
            try:
                comment.reply(message)
                self.cursor.execute(config.SQL_ADD_COMMENT.format(
                    tablename=self.tablename,
                    id=comment.fullname,
                    subreddit=comment.subreddit,
                    now=datetime.now()
                ))
                self.conn.commit()
                print("Replied.")
                comment.mark_read()
            except praw.exceptions.APIException as err:
                print(err)

    def clean_up(self):
        self.new_comments = []
        self.outputs = []
        self.messages = []
        self.codes = []

    def run(self):
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
    bot = praw.Reddit('pythonBot')
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    runners = []

    for language in config.LANGUAGES.values():
        runners.append(BotRunner(cursor, bot, conn, language))
    while True:
        try:
            for runner in runners:
                runner.run()
        except Exception as e:
            with open("log.txt", "a+") as f:
                print(str(e))
                f.write(str(e)+"\n")