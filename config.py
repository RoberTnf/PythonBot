"""Constants, SQL connectors"""

from os import environ

# execution params
TEST = True
MAX_TIME = 1
ALLOWED_USERS = ["AgressiveYorkshire"]
ALLOWED_SUBREDDITS = ["testingground4bots"]

#sqlite3
DB_FILE = "database.db"

SQL_CREATE_TABLE_REDDIT = """
CREATE TABLE IF NOT EXISTS {tablename} (
    id TEXT PRIMARY KEY,
    subreddit TEXT NOT NULL,
    created_at TIMESTAMP
);
"""
SQL_SEARCH = """SELECT * FROM {tablename} WHERE id='{id}'"""
SQL_ADD_COMMENT = """INSERT INTO {tablename} (id, subreddit, created_at) VALUES ('{id}', '{subreddit}', '{now}')"""

# Reddit params
NUMBER_OF_POSTS = 100
CALLSIGN = "!python"

OUTPUT_TEMPLATE = """
{number}:

{output}
"""
SIGNATURE = """
***
^^I'm ^^a ^^bot, ^^check ^^me ^^out ^^at: ^^https://github.com/RoberTnf/BookBot
"""
