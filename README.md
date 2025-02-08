# Hack the North Backend Challenge Submission

This project acts as a submission to my application to be on Hack The North's 2025 Organizing team.

---

## API Description

This REST API backend is written with Python and Flask, with a database created with SQLite (and SQLAlchemy ORM). It acts as a server that would store and work with the HTN user data. The database currently holds two connected tables: the first contains all hackers' main data, while the second includes the scans with individual activities occurring during the hackathon.

### Endpoint Features

The API can handle direct HTTP requests to:

- Output all hackers' data - including name, email, phone, badge_code, and information on scans
- Output the listed data for one specified hacker
- Update subsets of the database fields with valid information
- Add scans (complete with name, category, and time scanned), to the "scans" table with unique combinations of hacker badge codes and activity names
- Output aggregate data about the scans for each activity, with optional query parameters to filter results

In addition to these required features, I decided to include simple endpoints to **create** and **delete** hackers from the database, as I believe this could be useful during the hackathon if singular requests must be made to update a participant's inclusion status. The API can thus:

- Write to the "hackers" table with a new hacker's information
- Remove a hacker from the table, should circumstances need it (e.g. badge was lost or no longer works)

---

## Assumptions

Aside from the given rules in the instructions, I made the following assumptions:

- All badge_codes are strings following the specified format (four words connected with dashes), and that they can be set as unique fields that are NOT null in the table for "hackers" of the database. Badge codes, once assigned, should not be changed (it is an immutable identifier).

- Names and phone numbers, however, can be duplicated across different hackers in the table. They are all strings as well.

- Phone numbers do not need to follow a consistent format (like dashes and spacing).

- Emails are unique and not null. Email updates must maintain uniqueness across all users.

- A hacker can have many scans for different activities, but no same hacker has multiple scans for the same activity. A hacker can have no scans at all. There are no restrictions on how many activities a user can attend. Activities don't have explicit start/end times.

- All timestamps are in the same timezone, based on the same formatting in the given example data. Timestamps are in ISO 8601 format, as stated in the challenge instructions. All timestamps are from the same year, but the events span multiple days, as consistent with a hackathon. I also do not think I have to handle timezone conversions.

- Scans are ordered chronologically in the dataset, but this is simply as a result of new scans being added later than previous ones. Scan records are unchangeable once created.

- `Updated_at` in the "hackers" table will be in timestamp format, according to the last time that any of the hacker's information was modified.
- Each activity belongs to only one category, and no two categories have activities of the same name (because `activity_name` is unique across all scans - which is why it is used as an identifier).

- `activity_name` and `activity_category` are strings (TEXT for SQL). The names use underscores instead of spaces so that they are one word. Activity names and categories are case-sensitive.

- A user's presence in "scans" should be concurrent with their existence in "hackers."

- I am also assuming that there is no need to validate email addresses, name of activities, phone numbers, and that I do not need to maintain a history record of user information that was changed.

---

## Important Decisions

### Tech Stack
- Going into this challenge with no API development experience, I put extensive thought into my decision between REST and GraphQL, and ultimately chose the former for its simplicity and shorter HTTP requests.

- Python is my first and strongest language, so I wrote code with the Python/Flask lanaguage and framework duo in my VS Code environment.

- I used componenents of the provided boilerplate, but time constraints resulted in my decision not to incorporate Docker while exporting my project.

### Database
- Upon practicing creating databases, I noticed that an integer id is often used for the PRIMARY KEY in SQL tables. However, having this extra number field was less convenient when printing the hackers' info in my endpoints. I decided to use `badge_codes` as the primary key, as it was already defined to be unique for all users, and because it is the basis for the scanning functionality (as opposed to the email, which was also unique but contained not as useful information in this context). I further set the badge_code to be NOT NULL, as I find it most logical that only a hacker that has obtained their badge (and non-empty badge_code) can participate in the hackathon. This means that five of the hackers in the example_data.json file were not added to the database (you see this when you run script.py).

- In my database, I created two tables that encompassed the core required functionality. The "scans" table is connected to the main "hackers" info table via a foreign key so that all scans can be attributed to both an activity and a hacker. I also found it logical that one user should only need to scan into one activity once, so the primary key for "scans" is a composite of `activity_name` and `badge_code`, so that no pair can be duplicated. I acknowledge the limitation this might have on events where frequent entry and exit is allowed. 

- Another consideration is not to order the database by name or badge_code (however, "scans" will automatically be ordered chronologically when new scans are added to the bottom of the table). This is because I do not believe ordering will increase efficiency of the program when running commands such as getting aggregate data - the database is not meant to be large (only some thousands of hackers in the table) and should be fast to search through. However, organization of hackers may become relevant if HTN participant sizes increase on a large scale.

### Coding the Endpoints
- I decided to keep each endpoint in their individual functions, regardless of some having the same or similar routes - their HTTP methods would be different. Endpoints were all written in the same main file, app.py, for cohesiveness and convenience.

- Since SQL's TIMESTAMP function did not output timestamps with milliseconds, I implemented, with datetime, a function get_exact_time that provides the timestamp in exact ISO 8601 format. This function was written in two files instead of imported, as it was very short (importing files to one another caused errors that were not worth solving).

- output of the get all hackers function puts the scnas in a list, which could not be formatted otherwise

- decided to manually select the parts of scans that are to be outputted to fit the user information
- do not have to add a scans section for a new created hacker, will automatically be done when a scan is actually made
- however, the big json file includes the scans, sort of an initializing scan as if they just checked into the event
- due to my time constraints, i chose not to validate all user inputs, like how i assumed that min_frequency is an integer less than or equal to max_frequency, or that user emails and phones had correct characters (e.g. @gmail.com) - this is also not very important, as data intake software such as Google Forms would also be able to check if dates and emails/URLs are correct
- before in the testing, trying to add a hacker that was already added would give me the error, sqlite3.IntegrityError: UNIQUE constraint failed: hackers.badge_code, after which all other commands would have resulted in an error ending with "sqlite3.OperationalError: database is locked"


- but since doing a lot of looping and searching individually, i can make another sql database table with the number of activities to enable functionality like ensuring only 1 mignight snack event per person and checking if the person's id name or email is alreday on the event in the activities table, which has individual activity ids for a reason
- also good for if the hackathon wants to expand or if the users are scanning 4390439 times
- questions i needed to consider: what happens when given an invalid user for update, delete, or get_hacker? would i let the sql error occur, or would i need to create a testcase for that and ouput my own custom error message?

- in my update_users function for the updating endpoint, i needed to check if a change was made and whether it was valid in the fields where ids needed to be unique, and if they were not NULL, and then change only them, in the end there are only 6 fields, 4 of which were changeable (scans would be changed in a different function, and updated_at would be automatically changed only if another field was updated)

- i started by making the main identifier for each hacker to be a number, incremented by 1 for each additional hacker, but that was just unnecessary information, so i opted to use badge_codes, as they would be unique and could probably send the most information for future functionality

- while i could have chosen to close the connection and not update any of the fields requested after finding that email is invalid, i chose to proceed only by not updating email and assuming that the other information was correct. this is so that each of the other fields (phone, name) could be updated immediately after so i would not have to store a list of commands i would later give to the sql connection


---

## Setup Instructions:

Here's how you can set up my API in the same environment I used to develop it:

1. Set up the Python virtual environment for use on a local machine

   `python3 -m venv venv`

   `source venv/bin/activate` (for macOS)

2. Inside the venv, install all requirements

   `pip install -r requirements.txt`

3. From a new terminal, ensure that the current directory is `htn`

   `cd ~/htn`

4. Run the file called `create_database.py` to initialize a database in the directory

   `python create_database.py`

5. If to be used immediately with a dataset, run the file called `script.py` with a JSON file containing a dataset of hackers' information. In this case, the sample file is located inside `json_data`:

   `python script.py json_data/example_data.json`

6. Run the main program contained in `app.py`

   `python app.py`

If everything went smoothly, you should see something like this:

![image of successful result after running app.py](image.png)

Now, the API is ready to be tested and for use.

---

## Instructions for Use

Although this may not be the same method used for evaluation of my API, here is how I tested my endpoints:

On my computer system, I open a terminal window. I used `curl` to send in HTTP requests, so my commands are as follows:

- To get all of the hacker data (`get_hackers` in `app.py`) in JSON format, I run `curl -X GET http://127.0.0.1:5000/hackers`

- To create a new hacker (`create_hacker`) with example badge code ABC123 (note that this does not adhere by the HTN badge_code naming system), I run `curl -X POST http://127.0.0.1:5000/hackers \ -H "Content-Type: application/json" \ -d '{"name": "John Doe", "email": "johndoe@example.com", "phone": "123-456-7890", "badge_code": "ABC123"}'`. The following commands work with the example hacker with badge code ABC123.

- To delete a hacker (`delete_hacker`), for example the one I just created, I run `curl -X DELETE http://127.0.0.1:5000/hackers/ABC123`

- To get a specific hacker's information (`get_hacker`), if they exist, I run `curl -X GET http://127.0.0.1:5000/hackers/ABC123`

- To update a specific hacker's information (`update_hacker`), I run `curl -X PUT http://127.0.0.1:5000/hackers/ABC123 \ -H "Content-Type: application/json" \ -d '{ "name": "Johnathan Doe", "email": "johnny@example.com", "phone": "987-654-3210"}'`. Note that I do not have to provide a change to ALL fields, any subset of the updateable fields will suffice.

- To add a scan for a hacker (`add_scan`), I run `curl -X PUT http://127.0.0.1:5000/hackers/ABC123 \ -H "Content-Type: application/json" \ -d '{"name": "Johnathan Doe", "email": "johnny@example.com", "phone": "987-654-3210"}'`

- To retrieve scan data (`scan_data`), with optional query parameters, I run `curl -X GET "http://127.0.0.1:5000/scans?min_frequency=1&max_frequency=50&activity_category=Learning"`

It is worth noting that although I have checked for several instances of invalid request entries (e.g. get_hacker being given a hacker badge_code that does not exist in the database), I am assuming that input will usually be valid. I acknowledge that if an invalid input is given to code without error-checking measures, it can break the SQL database definition rules that I have set (e.g. UNIQUE fields like activity_name in "scans" table), and that further commands will lead to an error like `sqlite3.OperationalError: database is locked` for the rest of the session.

---

## Last Updated

Friday, February 7th, 2025

---

## Credits

Author: This project was created and developed by Angela Zhuang

Core Works Referenced:

- https://www.youtube.com/watch?v=Sf-7zXBB_mg
- https://www.youtube.com/watch?v=PTfZcN20fro
- https://labex.io/tutorials/flask-building-flask-rest-api-with-sqlite-298842
- https://www.postman.com/api-platform/api-documentation/

Thank you for taking the time to review my API!
