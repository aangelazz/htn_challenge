import sqlite3
import json
import sys
from datetime import datetime # function imported to retrieve exact ISO 8901 timestamp


## Gets current timestamp with millisecond precision
def get_exact_time():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')


## Look for JSON file
if len(sys.argv) != 2:
    print("Error: JSON file not found")
    sys.exit(1)


file = sys.argv[1] # retrieving the JSON file


## loading data from JSON file
try:
    with open(file, "r") as json_file:
        hacker_data = json.load(json_file)
except FileNotFoundError:
    print("Error: JSON file not found")
    sys.exit(1)
except json.JSONDecodeError:
    print("Error: invalid JSON file could not be read")
    sys.exit(1)


## Connect to SQLite database
connection = sqlite3.connect("participants.db")
cursor = connection.cursor()


## Insert hackers into the database
added_count = 0 # to keep track of number of hackers added to database
scan_count = 0

for hacker in hacker_data:
    name = hacker.get("name", "Unknown")
    email = hacker.get("email", "Unknown").strip().lower() # since SQL is case-sensitive, make sure all emails are lowercase with no extra spaces
    phone = hacker.get("phone", None)
    badge_code = hacker.get("badge_code", None)
    timestamp = get_exact_time()

    try:
        cursor.execute('''
            INSERT INTO hackers (name, email, phone, badge_code, updated_at) 
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, phone, badge_code, timestamp))
        added_count += 1

        scans = hacker.get("scans", [])
        for scan in scans:
            activity_name = scan.get("activity_name", "")
            activity_category = scan.get("activity_category", "")
            scanned_at = scan.get("scanned_at", "")

            if activity_name and activity_category and scanned_at:
                cursor.execute('''
                       INSERT INTO scans (badge_code, activity_name, activity_category, scanned_at) VALUES (?, ?, ?, ?) ''',
                       (badge_code, activity_name, activity_category, scanned_at))
                scan_count += 1
                       
        
    except sqlite3.IntegrityError:
        print("\nSkipping hacker: either email or badge code is already used, or NULL")
        print(f"Name: {name}\nEmail: {email}\nBadge Code: '{badge_code}'\n")


## Commit changes and close SQL database connection
connection.commit()
cursor.close()
connection.close()


print("Success, ", added_count," new hackers added successfully with ", scan_count, " total new scans")