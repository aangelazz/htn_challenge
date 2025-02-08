from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

app = Flask(__name__)


## Gets current timestamp with millisecond precision
def get_exact_time():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')


## Endpoint to retrieve all the hackers and their information
@app.route("/hackers", methods = ['GET'])
def get_hackers():
    ## Connection to the database
    connection = sqlite3.connect('participants.db')
    cursor = connection.cursor()

    ## SQL query that retrieves all hackers
    cursor.execute('SELECT * FROM hackers')
    hackers = cursor.fetchall()

    ## Fetch all scans for all hackers
    cursor.execute('SELECT badge_code, activity_name, activity_category, scanned_at FROM scans')
    scans = cursor.fetchall()

    ## Formatting all scans by hackers' badge_code
    scans_per_hacker = {}
    for scan in scans:
        badge_code = scan[0]
        if badge_code not in scans_per_hacker:
            scans_per_hacker[badge_code] = []
        scans_per_hacker[badge_code].append({
            "activity_name": scan[1],
            "activity_category": scan[2],
            "scanned_at": scan[3]
        })
        

    ## Putting together list to format all hackers' data
    hackers_list = []
    for hacker in hackers:
        hacker_data = {
            "name": hacker[0],
            "email": hacker[1],
            "phone": hacker[2],
            "badge_code": hacker[3],
            "updated_at": hacker[4],
            "scans": scans_per_hacker.get(hacker[3], [])
        }
        hackers_list.append(hacker_data)


    ## Closing the cursor and database connection
    cursor.close()
    connection.close()


    ## returning all of the hackers as JSON
    return jsonify(hackers_list)


## Endpoint to create a new hacker, in case one was not registered properly
@app.route('/hackers', methods=['POST'])
def create_hacker():
    ## Get the hacker data 
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    badge_code = data.get('badge_code')
    timestamp = get_exact_time()

    ## Connect to the database
    connection = sqlite3.connect('participants.db')
    cursor = connection.cursor()

    ## Execute the SQL query to insert a new hacker
    cursor.execute('INSERT INTO hackers (name, email, phone, badge_code, updated_at) VALUES (?, ?, ?, ?, ?)', 
                   (name, email, phone, badge_code, timestamp))
    connection.commit()

    ## Close the cursor and the database connection
    cursor.close()
    connection.close()

    ## Return a success message
    return jsonify({'message': 'New Hacker created successfully'})



## Endpoint to delete a hacker from the database
@app.route('/hackers/<string:hacker_id>', methods=['DELETE'])
def delete_hacker(hacker_id):
    ## Connect to the database
    connection = sqlite3.connect('participants.db')
    cursor = connection.cursor()

    # Get exact ISO 8601 format of time with function from script.py
    timestamp = get_exact_time()

    ## Execute the SQL query to update the updated_at before deletion (in case hacker is somehow backed up)
    cursor.execute('UPDATE hackers SET updated_at = ? WHERE badge_code = ?', (timestamp, hacker_id))
    connection.commit()


    ## Execute the SQL query to delete the hacker
    cursor.execute('DELETE FROM hackers WHERE badge_code = ?', (hacker_id,))
    connection.commit() 


    ## Close the cursor and the database connection
    cursor.close()
    connection.close()

    ## Return message
    return jsonify({'message': 'Hacker removed successfully'})




## Endpoint to retrieve a hacker by their specific ID (badge_code)
@app.route('/hackers/<string:hacker_id>', methods = ['GET'])
def get_hacker(hacker_id):

    ## Connect to the database
    connection = sqlite3.connect('participants.db')
    cursor = connection.cursor()
    

    ## SQL command to retreive the hacker by ID (badge_code)
    cursor.execute('SELECT * FROM hackers WHERE badge_code = ?', (hacker_id,))
    hacker = cursor.fetchone()

    if not hacker:
        cursor.close()
        connection.close()
        return jsonify({"error": "Hacker not found"}), 404

    # Fetch all scans associated with the hacker
    cursor.execute("SELECT activity_name, activity_category, scanned_at FROM scans WHERE badge_code = ?", (hacker_id,))
    scans = cursor.fetchall()


    ## Close the cursor and connection for database
    cursor.close()
    connection.close()

    # Format response data
    hacker_data = {
        "name": hacker[0],
        "email": hacker[1],
        "phone": hacker[2],
        "badge_code": hacker[3],
        "updated_at": hacker[4],
        "scans": [{"activity_name": scan[0], "activity_category": scan[1], "scanned_at": scan[2]} for scan in scans]
    }

    return jsonify(hacker_data)
    
    

## Endpoint that updates an existing hacker's information
@app.route('/hackers/<string:hacker_id>', methods = ['PUT'])
def update_hacker(hacker_id):
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    
    ## Check that at least one field is being updated, otherwise move on to output unchanged data information
    if not any([name, phone, email]):
        print("All information up to date, no changes made!")
    else:

        ## Connection to the database
        connection = sqlite3.connect('participants.db')
        cursor = connection.cursor()

        ## Get exact timestamp
        timestamp = get_exact_time()

        ## SQL query to update the hacker's information, gone by each field
        if name:
            cursor.execute('UPDATE hackers SET name = ? WHERE badge_code = ?', (name, hacker_id))
            connection.commit()


        if phone:
            cursor.execute('UPDATE hackers SET phone = ? WHERE badge_code = ?', (phone, hacker_id))
            connection.commit()


        if email:
            email = email.strip().lower()  # Make sure email is in lowercase with no extra spaces
            
            ## Get existing email from hacker's information
            cursor.execute("SELECT badge_code FROM hackers WHERE email = ? AND badge_code != ?", (email, hacker_id))
            existing_email = cursor.fetchone()

            ## Check validity of email
            if email == "":
                print("Email not changed, given email was invalid")
            elif existing_email:
                print("Email is already in use, was not changed")
            else:
                cursor.execute('UPDATE hackers SET email = ? WHERE badge_code = ?', (email, hacker_id))
                connection.commit()


        ## Update Timestamp after making all changes
        cursor.execute('UPDATE hackers SET updated_at = ? WHERE badge_code = ?', (timestamp, hacker_id))
        connection.commit()
    

        ## Close cursor and connection to database
        cursor.close()
        connection.close()


        print("Valid hacker information updated succesfully")
        
    return get_hacker(hacker_id)

## Endpoint to add scan for a hacker
@app.route('/scan/<string:hacker_id>', methods=['PUT'])
def add_scan(hacker_id):
    data = request.get_json()
    name = data.get("activity_name")
    cat = data.get("activity_category")

    if not name or not cat:
        return jsonify({"error":"no name or category was given for the activity"}), 400
    
    ## Connect to the database
    connection = sqlite3.connect('participants.db')
    cursor = connection.cursor()

    # Check if hacker exists
    cursor.execute("SELECT badge_code FROM hackers WHERE badge_code = ?", (hacker_id,))
    hacker = cursor.fetchone()

    if not hacker:
        cursor.close()
        connection.close()
        return jsonify({"error":"hacker was not found"}), 400


    ## Get current timestamp
    timestamp = get_exact_time()

    ## Insert scan into scans table
    cursor.execute('''INSERT INTO scans (badge_code, activity_name, activity_category, scanned_at) VALUES (?, ?, ?, ?)''',
                     (hacker_id, name, cat, timestamp))

    ## Update updated_at in hackers table
    cursor.execute(''' UPDATE hackers SET updated_at = ? WHERE badge_code = ?''', (timestamp, hacker_id))

    ## Commit changes and close connection
    connection.commit()
    cursor.close()
    connection.close()

    print("Scan recorded successfully")

    return get_hacker(hacker_id)


## Endpoint that provides scan data
@app.route("/scans", methods = ['GET'])
# MAKE SURE THAT WHEN RUNNING WITH CURL IN TERMINAL, PUT COMMAND IN QUOTES SO CAN PARSE
#   e.g. curl -X GET "http://127.0.0.1:5000/scans?max_frequency=25&min_frequency=20&activity_category=activity"
def scan_data():
    min_frequency = request.args.get("min_frequency", type=int) # assumes that min_frequency is less than or equal to max_frequency
    max_frequency = request.args.get("max_frequency", type=int)
    activity_category = request.args.get("activity_category", type=str)

    ## Connect to the database
    connection = sqlite3.connect('participants.db')
    cursor = connection.cursor()

    ## SQL Query to get all activities' scan frequencies, will filter on them after
    query = '''SELECT activity_name, activity_category, COUNT(*) as frequency FROM scans'''

    ## Define the optionally included conditions for the results
    conditions = []
    parameters = []

    
    ## Go through each condition, and append to conditions and parameters if given
    if activity_category:
        conditions.append("activity_category = ?")
        parameters.append(activity_category)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY activity_name, activity_category"
    
    ## Frequency specifications
    frequencies = []
    if min_frequency is not None:
        frequencies.append("COUNT(*) >= ?")
        parameters.append(min_frequency)
    if max_frequency is not None:
        frequencies.append("COUNT(*) <= ?")
        parameters.append(max_frequency)


    if frequencies:
        query += " HAVING " + " AND ".join(frequencies)

    ## sending out query
    cursor.execute(query, parameters)
    results = cursor.fetchall()


    formatted = [
        {"activity_name": row[0], "activity_category": row[1], "frequency": row[2]}
        for row in results
    ]

    ## Close connection to database
    cursor.close()
    connection.close()

    return jsonify(formatted)


if __name__ == "__main__":
    app.run(debug=True)
