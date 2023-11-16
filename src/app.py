from flask import Flask, request, render_template, redirect, url_for, session, make_response, jsonify
from flask_session import Session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import secrets
from datetime import timedelta

import algorithms.bruteforce as BruteForceAlgorithm
import algorithms.nearestneighbor as NearestNeighborsAlgorithm
import algorithms.places_to_coordinates as CoordConverter

app = Flask(__name__)


app.config['SESSION_PERMANENT'] = False
# we could change this depending on if we want session data to be stored in a DB too
app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SESSION_FILE_THRESHOLD'] = 100

# must create DB on pythonanywhere first
app.secret_key = secrets.token_urlsafe(16)
 
# figure these out after we host it on pythonanywhere
# for now, I have it configured for my local host
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'myAdmin'
app.config['MYSQL_PASSWORD'] = 'mypassword'
app.config['MYSQL_DB'] = 'travelfast'

app.config.from_object(__name__)

Session(app)
mysql = MySQL(app)


user_credentials = {"Bob": "bobiscool", "John": "password"} # Just a placeholder for the real database system for now

user_locations = [] # Just a placeholder for the real database system for now
user_location_names = []

route_algorithm_method = BruteForceAlgorithm.best_route # Default computation method will be the BFA


# ------------ HOME PAGE --------------
@app.route('/')
def redirect_to_login():
    return render_template("login.html")



# ------------ LOGIN REQUEST --------------
# took inspiration for mysql functionality from https://www.geeksforgeeks.org/profile-application-using-python-flask-and-mysql/
@app.route('/login/', methods=["POST", "GET"])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form["username"]
        password = request.form["password"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mySQLCommand = 'SELECT * FROM travelfast.users WHERE username = \'' + username + '\' AND password = \'' + password + '\';'
        cursor.execute( mySQLCommand )
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'You\'re logged in!'
            return render_template("home.html", user = username, return_info = msg)
        else:
            msg = 'Incorrect username or password'
    return render_template("login.html", return_info = msg)
    
    
    
# ------------ LOGOUT --------------
# need to research more about sessions and how we are keeping track of the user in our code
@app.route('/logout/', methods=['POST'])
def logout():
    msg = ''
    if session['loggedin']:
        session['loggedin'] = False
        session['id'] = None
        session['username'] = None
        msg = 'You logged out'
    else:
        msg = 'You never logged in. Please login'
    return render_template("login.html", return_info = msg)



# ------------ CREATE ACCOUNT POST --------------
# took inspiration for mysql functionality from https://www.geeksforgeeks.org/profile-application-using-python-flask-and-mysql/
@app.route('/create_account/', methods=["POST", "GET"])
def create_account():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form["username"]
        password = request.form["password"]
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mySQLCommand = 'SELECT * FROM travelfast.users WHERE \'' + username + '\';'
        cursor.execute( mySQLCommand )
        account = cursor.fetchone()
        
        if account:
            msg = 'Username already exists'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Only characters and numbers allowed in username!'
        elif not username or not password:
            msg = 'Fill out the form'
        else:
            myConnection = mysql.connection
            insertCursor = mysql.connection.cursor()
            mySQLCommand = 'INSERT INTO travelfast.users (username, password) VALUES (\'' + username + '\', \'' + password + '\');' 
            insertCursor.execute( mySQLCommand )
            myConnection.commit()
            insertCursor.close()
            msg = 'Account created!'
            return render_template("login.html", return_info = msg)
    elif request.method == 'POST':
        msg = 'Please create an account to continue!'
    return render_template("account_create.html", return_info = msg)
    
    

# ------------ SAVE USER'S ROUTES --------------
# -Stores a user's route in the database
# -This route has no method for now
@app.route('/store_user_route/', methods=["POST", "GET"])
def store_user_route():
    msg = ''
    if session['loggedin']:
        user_id = session['id']
        blob = locations_to_blob()
        latitudes_blob = blob[0]
        longitudes_blob = blob[1]
        
        if latitudes_blob == None or longitudes_blob == None:
            msg = 'No locations to save'
            return render_template("route_finder.html", return_info = msg)
        
        myConnection = mysql.connection
        insertCursor = mysql.connection.cursor()
        mySQLCommand = 'INSERT INTO travelfast.routes (id, latitude, longitude) VALUES (\'' + user_id + '\',\'' + latitudes_blob + '\', \'' + longitudes_blob + '\');' 
        insertCursor.execute( mySQLCommand )
        myConnection.commit()
        insertCursor.close()
        
    msg = 'You must be logged in to save routes'
    return render_template("login.html", return_info="msg")

# helper to convert user_locations to a blob (a long string)
def locations_to_blob():
    lats = ''
    longs = ''
    for lat_long in user_locations:
        lats += (str(lat_long[0]) + ', ')
        longs += (str(lat_long[1]) + ', ')
    if len(lats) >= 3 and len(longs) >= 3:
        lats = lats[:-2]
        longs = longs[:-2]
    else:
        lats = None
        longs = None
    return [lats, longs]



# ------------ RETRIEVE USER'S ROUTES --------------
# -Stores a user's route in the database
# -This route has no method for now
@app.route('/retrieve_user_route/', methods=["POST", "GET"])
def retrieve_user_route():
    msg = ''
    if session['loggedin'] and request.method == 'POST': 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mySQLCommand = 'SELECT * FROM travelfast.routes WHERE id = \'' + session['id'] + '\';'
        cursor.execute( mySQLCommand )
        route = cursor.fetchone()
        if route:
            session['routes'] = route
            msg = 'We retrieved your routes'
            return render_template("home.html", return_info=msg) 
        msg = 'You have no routes saved'
        return render_template("home.html", return_info=msg)
    msg = 'You must be logged in to save routes'
    return render_template("login.html", return_info=msg)



@app.route('/temp_bypass_to_map/', methods=["POST", "GET"])
def to_map():
    return render_template("home.html", user = "TEMP", return_info = "TEMP")



@app.route('/temp_bypass_to_route_finder/', methods=["POST", "GET"])
def to_route_finder():
    return render_template("route_finder.html", return_info = "Your list of added locations will show up here!")



@app.route('/add_location_by_coords/', methods=["POST", "GET"])
def add_location_by_coords():
    try:
        latitude = float(request.form["latitude"])
        longitude = float(request.form["longitude"])
    except:
        return render_template("route_finder.html", return_info = "Unable to add most recent location. Did you input numbers to both fields?")
    
    
    user_locations.append([latitude, longitude])
    user_location_names.append("Unnamed")
    added_duplicate = False
    formatted_locations_string = "Place Locations: "
    formatted_names_string = "Place Names: "
    for i, location in enumerate(user_locations):
        if location[0] == latitude and location[1] == longitude and i != len(user_locations) - 1: # User tried to add duplicate location, ignored by skipping it entirely
            added_duplicate = True
            continue
        formatted_locations_string += f"Latitude: {location[0]}, Longitude: {location[1]} "
        formatted_names_string += user_location_names[i] + ", "
    if added_duplicate:
        user_locations.pop() # Remove the duplicate location
        user_location_names.pop()
    if (len(formatted_names_string) > 2):
        formatted_names_string = formatted_names_string[:-2] # removes last comma and space
    return render_template("route_finder.html", return_info = formatted_locations_string, place_names = formatted_names_string)



@app.route('/add_location_by_name', methods=["POST", "GET"])
def add_location_by_name():
    new_place_name = request.form["name"]
    new_lat_long_arr = CoordConverter.return_coords([new_place_name])[0]
    if (new_lat_long_arr == -1): # Invalid place, at least according to API
        return render_template("route_finder.html", return_info = "We failed to find a place corresponding to the most recently added name")
    
    latitude, longitude = new_lat_long_arr
    user_locations.append(new_lat_long_arr)
    user_location_names.append(new_place_name)
    added_duplicate = False
    formatted_locations_string = "Place Locations: "
    formatted_names_string = "Place Names: "
    for i, location in enumerate(user_locations):
        if location[0] == latitude and location[1] == longitude and i != len(user_locations) - 1: # User tried to add duplicate location, ignored by skipping it entirely
            added_duplicate = True
            continue
        formatted_locations_string += f"Latitude: {location[0]}, Longitude: {location[1]} "
        formatted_names_string += user_location_names[i] + ", "
    if added_duplicate:
        user_locations.pop() # Remove the duplicate location
        user_location_names.pop()
    if (len(formatted_names_string) > 2):
        formatted_names_string = formatted_names_string[:-2] # removes last comma and space
    return render_template("route_finder.html", return_info = formatted_locations_string, place_names = formatted_names_string)



@app.route('/clear_route_locations/', methods=["POST", "GET"])
def clear_locations():
    user_locations.clear()
    user_location_names.clear()
    return render_template("route_finder.html", return_info = "Route Locations Cleared.")



@app.route('/calculate_route/', methods=["POST", "GET"])
def calculate_route():
    try:
        inputted_algorithm_choice = request.form["algorithm_choice"]
    except: # No choice selected
        return render_template("route_finder.html", return_info = "Please select a route computation algorithm and try again")
    if inputted_algorithm_choice == "Brute Force":
        route_algorithm_method = BruteForceAlgorithm.best_route
    if inputted_algorithm_choice == "Nearest Neighbors":
        route_algorithm_method = NearestNeighborsAlgorithm.best_route   

    if len(user_locations) <= 1:
        return render_template("route_finder.html", return_info = "You must input at least two locations")
    route = route_algorithm_method(user_locations)
    sorted_indices = [i for i in range(len(route))]
    for i, location in enumerate(route):
        for j, inputted_location in enumerate(user_locations):
            if location == inputted_location:
                sorted_indices[i] = j

    formatted_route_string = "Full Route --> "
    for i, location in enumerate(route):
        formatted_route_string += f"Stop {i + 1}: "
        if (user_location_names[sorted_indices[i]] == "Unnamed"):
            formatted_route_string += f"Latitude {location[0]}, Longitude {location[1]}. "
        else:
            formatted_route_string += user_location_names[sorted_indices[i]] + ". "
    return render_template("route_finder.html", return_info = formatted_route_string)



@app.route('/return_route/', methods=["POST", "GET"])
def return_route():
    unused_request = request.get_json(force=True) # Don't actually need anything from the request but need to 'process' it
    route = BruteForceAlgorithm.best_route(user_locations) # Later this should just be a fetch from the database instead of recalculating every time
    response = make_response(jsonify(route))
    return response



@app.route('/delete_route/', methods=["POST"])
def delete_route():
    if session['loggedin']: #seshid
        user_id = session['id']
        route_id = request.form["route_id"]

        myConnection = mysql.connection
        deleteCursor = mysql.connection.cursor()
        mySQLCommand = 'DELETE FROM travelfast.routes WHERE user_id = %s AND id = %s'
        deleteCursor.execute(mySQLCommand, (user_id, route_id))
        myConnection.commit()
        deleteCursor.close()

        msg = 'Route deleted successfully!'
        return redirect(url_for('route_history'))

    msg = 'You must be logged in to delete routes'
    return render_template("login.html", return_info=msg)
