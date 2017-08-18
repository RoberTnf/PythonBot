
#!/usr/bin/env python3

"""
Reddit bot runner.
"""
from datetime import datetime
import sqlite3
import praw
import praw.models
import requests
from helpers import Interpreter, timeout_handler, TimeoutException
import signal
import config

# https://stackoverflow.com/questions/25027122/break-the-function-after-certain-time
# Change the behavior of SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)

class BotRunner(object):

    def __init__(self, cursor, bot, conn, callsign=config.CALLSIGN, tablename="comments"):
        self.tablename = tablename
        self.cursor = cursor
        self.bot = bot
        self.callsign = callsign
        self.new_comments = []
        self.outputs = []
        self.interpreter = Interpreter()
        self.messages = []
        self.conn = conn

        cursor.execute(config.SQL_CREATE_TABLE_REDDIT.format(tablename=self.tablename))

    def get_new_comments(self):
        request = requests.get('https://api.pushshift.io/reddit/search?q=%22{}%22&limit=100'\
            .format(self.callsign), headers = {'User-Agent': 'PythonBot Agent'})
        json = request.json()
        raw_comments = json["data"]
        comments = []

        for rawcomment in raw_comments:
            # object constructor requires empty attribute
            rawcomment['_replies'] = ''
            if self.callsign in rawcomment["body"].lower():
                comment = Comment(self.bot, _data=rawcomment)
                if not comment.was_replied(self.tablename, self.cursor)\
                    and comment.author not in config.BANNED_USERS\
                    and comment.subreddit in config.ALLOWED_SUBREDDITS:
                    comments.append(comment)

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
                        code += "\n" + line[4:]
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
                    self.interpreter.clear_files()
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
                messages[-1] += config.OUTPUT_TEMPLATE.format(number=i+1, output=sub_output)
        self.messages = messages

    def reply(self):
        for (comment, message) in zip(self.new_comments, self.messages):
            comment.reply(message)
            self.cursor.execute(config.SQL_ADD_COMMENT.format(
                tablename=self.tablename,
                id=comment.fullname,
                subreddit=comment.subreddit,
                now=datetime.now()
            ))
            self.conn.commit()

    def run(self):
        self.get_new_comments()
        self.get_code_from_comments()
        self.execute_codes()
        self.get_messages_from_outputs()
        self.reply()


class Comment(praw.models.Comment):
    def was_replied(self, tablename, cursor):
        rows = cursor.execute(config.SQL_SEARCH.format(
            tablename=tablename, id=self.fullname))
        return bool(rows.fetchall())


if __name__ == "__main__":
    bot = praw.Reddit('pythonBot')
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    runner = BotRunner(cursor, bot, conn, callsign="!python")
    runner.run()

