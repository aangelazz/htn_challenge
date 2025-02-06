# ## HackTheBackend

This project acts as a submission to my application to be on Hack The North's 2025 Organizing team.

---

Credits
Author: This project was created and developed by Angela Zhuang, with help only from online resources and

---

API Description

---

Assumptions

- badge codes cannot be duplicated, nor can they be NULL: there were 5 such users in the example_data.json file that had null badge codes

---

Important Decisions

- Splitting each endpoint into individual functions, regardless of them being in the same route
  Endpoints all in the same main file, app.py, to ensure cohesiveness
- adding, with datetime, a function that prints in the exact format of the given dataset (SQL default time does not record milliseconds)
- in my database, is one table enough or am i doing multiple tables or just one - and then how am i ordering the database? order might be faster but not necessarily (since theres many fields, i might try to order it on specific keys), which case
  think about the wyas i would use the fdatabase
  what types of data points do i add key
  e.g. how many people attended the coffee chat/specific event today? go see how many people (searching off of something that might not usually be a key)

considerations: for the searching the database, might be able to just search the entire massive big database if the users are small enough, just 1000 participants can be fast enough for the program

- but since doing a lot of looping and searching individually, i can make another sql database table with the number of activities to enable functionality like ensuring only 1 mignight snack event per person and checking if the person's id name or email is alreday on the event in the activities table, which has individual activity ids for a reason
- also good for if the hackathon wants to expand or if the users are scanning 4390439 times
- questions i needed to consider: what happens when given an invalid user for update, delete, or get_hacker? would i let the sql error occur, or would i need to create a testcase for that and ouput my own custom error message?

- in my update_users function for the updating endpoint, i needed to check if a change was made and whether it was valid in the fields where ids needed to be unique, and if they were not NULL, and then change only them, in the end there are only 6 fields, 4 of which were changeable (scans would be changed in a different function, and updated_at would be automatically changed only if another field was updated)

- i started by making the main identifier for each hacker to be a number, incremented by 1 for each additional hacker, but that was just unnecessary information, so i opted to use badge_codes, as they would be unique and could probably send the most information for future functionality

- while i could have chosen to close the connection and not update any of the fields requested after finding that email is invalid, i chose to proceed only by not updating email and assuming that the other information was correct. this is so that each of the other fields (phone, name) could be updated immediately after so i would not have to store a list of commands i would later give to the sql connection

- reqriting functions like get_exact_time in each file because very short and did not need a separate file for it, also do not need to import it every time, but cannotn import from one file (e.g. i did that with script.py into app.py but when running app.py, it would import script.py, exiting and forcing the app.py to have script.py's functionality)
-
- for scans, i am creating a composite key so that the unique identifier activity_name can be scanned multiple times, given that it is not with a badge_code that has been scanned for that activity before.

- output of the get all hackers function puts the scnas in a list, which could not be formatted otherwise

- decided to manually select the parts of scans that are to be outputted to fit the user information
- do not have to add a scans section for a new created hacker, will automatically be done when a scan is actually made
- however, the big json file includes the scans, sort of an initializing scan as if they just checked into the event

---

Setup Instructions:

- Here's how to connect this to my frontend

---

Instructions for Use

---

Tests

---

Last Updated: Friday, February 7th, 2025
