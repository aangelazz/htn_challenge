"""
This file creates the database "participants.db" with which the API can be used in conjunction
"""

import sqlite3


## Connection to the database
connection = sqlite3.connect('participants.db')
## Creating a cursor object to execute SQL statements
cursor = connection.cursor()


## Creating a table called "hackers"
cursor.execute('''CREATE TABLE IF NOT EXISTS hackers (
               name TEXT NOT NULL,
               email TEXT UNIQUE NOT NULL,
               phone TEXT,
               badge_code TEXT PRIMARY KEY UNIQUE NOT NULL,
               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''') ## add the NOT NULL and UNIQUE requirements to ensure no duplicates for emails, and badge_code is the primary key
## Commit the changes to the database
connection.commit()


## Create a "scans" table, with primary key being composite of both the badge_code and activity_name
cursor.execute('''
    CREATE TABLE IF NOT EXISTS scans (
        badge_code TEXT NOT NULL,
        activity_name TEXT NOT NULL,
        activity_category TEXT NOT NULL,
        scanned_at TEXT NOT NULL,
        PRIMARY KEY (badge_code, activity_name),
        FOREIGN KEY (badge_code) REFERENCES hackers(badge_code) ON DELETE CASCADE)''')
## Commit the changes to the database
connection.commit()


## Close the cursor and the database connection
cursor.close()
connection.close()