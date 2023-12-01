from flask import Flask, request, render_template, redirect, url_for, session, make_response, jsonify
from flask_session import Session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import secrets
from datetime import timedelta
import json

import algorithms.bruteforce as BruteForceAlgorithm
import algorithms.nearestneighbor as NearestNeighborsAlgorithm
import algorithms.genetic as GeneticAlgorithm
import algorithms.dynamic as DynamicProgAlgorithm
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


user_locations = []
user_location_names = []

has_added_personal_location = False # Set to true if the user uses the current location feature

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
            #return render_template("home.html", user = username, return_info = msg) NO LONGER USING home.html (functionality has been fully migrated to route_finder.html)
            return render_template("route_finder.html", return_info = "Your list of added locations will show up here!", user_welcome = "Welcome " + username + "!")
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
        session['routes'] = None
        msg = 'You have been logged out.'
        #Reset instance variables back to defaults
        global user_locations, user_location_names, has_added_personal_location
        user_location_names = []
        user_locations = []
        has_added_personal_location = False
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
        elif not username or not password:
            msg = 'Please enter both a username and password!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Only characters and numbers allowed in username!'
        else:
            myConnection = mysql.connection
            insertCursor = mysql.connection.cursor()
            mySQLCommand = 'INSERT INTO travelfast.users (username, password) VALUES (\'' + username + '\', \'' + password + '\');' 
            insertCursor.execute( mySQLCommand )
            myConnection.commit()
            insertCursor.close()
            msg = 'Account created!'
            return render_template("login.html", return_info = msg)
    #elif request.method == 'POST':
        #msg = 'Please create an account to continue!'
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
        location_names_blob = blob[2]
        
        if latitudes_blob == None or longitudes_blob == None:
            msg = 'No locations to save'
            return render_template("route_finder.html", return_info = msg)
        
        myConnection = mysql.connection
        insertCursor = mysql.connection.cursor()

        #First deletes the previously saved route if any for the user
        mySQLCommand = 'DELETE FROM travelfast.routes WHERE user_id = \'' + str(user_id) + '\';'
        insertCursor.execute( mySQLCommand )

        #Then save the new route as a replacement to that row
        mySQLCommand = 'INSERT INTO travelfast.routes (user_id, latitude, longitude, location_names) VALUES (\'' + str(user_id) + '\',\'' + latitudes_blob + '\', \'' + longitudes_blob + '\', \'' + location_names_blob + '\');' 
        insertCursor.execute( mySQLCommand )
        myConnection.commit()
        insertCursor.close()
        return render_template("route_finder.html", return_info = "Your route has been saved!")
        
    msg = 'You must be logged in to save routes'
    return render_template("login.html", return_info = msg)

# helper to convert user_locations to a blob (a long string)
def locations_to_blob():
    lats = ''
    longs = ''
    names = ''
    if len(user_locations) == 0:
        return [None, None]
    route = route_algorithm_method(user_locations)
    for lat_long in route:
        lats += (str(lat_long[0]) + ', ')
        longs += (str(lat_long[1]) + ', ')
    for name in user_location_names:
        names += name + ', '
    if len(lats) >= 3 and len(longs) >= 3:
        lats = lats[:-2]
        longs = longs[:-2]
        names = names[:-2]
    else:
        lats = None
        longs = None
        names = None
    return [lats, longs, names]

# helper to convert database strings back to route lat long pairs and user_location_names
def db_return_to_locations_and_names(database_map): # returns 2-tuple, first item is route locations, second is user_location_names
    latitudes = database_map['latitude'].decode().split(", ")
    longitudes = database_map['longitude'].decode().split(", ")
    location_names = database_map['location_names'].decode().split(", ")
    location_lat_long_pairs = []
    for lat, long in zip(latitudes, longitudes):
        location_lat_long_pairs.append([lat, long])
    return (location_lat_long_pairs, location_names)



# ------------ RETRIEVE USER'S ROUTES --------------
# -Stores a user's route in the database
# -This route has no method for now
@app.route('/retrieve_user_route/', methods=["POST", "GET"])
def retrieve_user_route():
    msg = ''
    if session['loggedin'] and request.method == 'POST': 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mySQLCommand = 'SELECT * FROM travelfast.routes WHERE user_id = \'' + str(session['id']) + '\';'
        cursor.execute( mySQLCommand )
        route = cursor.fetchone()
        if route:
            session['routes'] = route
            route_locations, route_names = db_return_to_locations_and_names(session['routes'])
            formatted_route_string = "Full Route --> "
            for i, location in enumerate(route_locations):
                formatted_route_string += f"Stop {i + 1}: "
                if (route_names[i] == "Unnamed"):
                    formatted_route_string += f"Latitude {location[0]}, Longitude {location[1]}. "
                else:
                    formatted_route_string += route_names[i] + ". "
            return render_template("route_finder.html", return_info = formatted_route_string)
        msg = 'You have no route saved!'
        return render_template("route_finder.html", return_info=msg, user_welcome = msg)
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

@app.route('/add_user_current_location', methods=["POST", "GET"])
def add_user_current_location():
    global has_added_personal_location # Not really sure why this is needed just for this boolean and not the other globals but this fixes an error
    if has_added_personal_location: # They've already added their own location
        return render_template("route_finder.html", return_info = "You've already added your current location to the route.")
    has_added_personal_location = True

    latitude, longitude = request.get_json(force=True)
    user_locations.append([latitude, longitude])
    user_location_names.append("Your Current Location")
    added_duplicate = False
    for i, location in enumerate(user_locations):
        if location[0] == latitude and location[1] == longitude and i != len(user_locations) - 1: # User tried to add duplicate location, ignored by skipping it entirely
            added_duplicate = True
            continue
    if added_duplicate:
        user_locations.pop() # Remove the duplicate location
        user_location_names.pop()
        has_added_personal_location = False
    return make_response(jsonify("unimportant")) # never going to use what's sent back so dummy value is used

@app.route('/user_location_added_follow_up/', methods=["POST", "GET"])
def follow_up_locations_list_display():
    formatted_locations_string = "Place Locations: "
    formatted_names_string = "Place Names: "
    for i, location in enumerate(user_locations):
        formatted_locations_string += f"Latitude: {location[0]}, Longitude: {location[1]} "
        formatted_names_string += user_location_names[i] + ", "
    if (len(formatted_names_string) > 2):
        formatted_names_string = formatted_names_string[:-2] # removes last comma and space
    return render_template("route_finder.html", return_info = formatted_locations_string, place_names = formatted_names_string)

@app.route('/clear_route_locations/', methods=["POST", "GET"])
def clear_locations():
    global has_added_personal_location
    user_locations.clear()
    user_location_names.clear()
    has_added_personal_location = False
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
    if inputted_algorithm_choice == "Dynamic Programming":
        route_algorithm_method = DynamicProgAlgorithm.best_route
    if inputted_algorithm_choice == "Genetic Algorithm":
        route_algorithm_method = GeneticAlgorithm.best_route   

    if len(user_locations) <= 1:
        return render_template("route_finder.html", return_info = "You must input at least two locations")
    session['routes'] = None # User is now using new calculated route not a loaded route from database
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
    route = []
    if session['routes']: # If the user loaded a route from the database and wants to show that this will be non-null
        route, names = db_return_to_locations_and_names(session['routes']) # names isn't important for this so it's unused
    else:
        route = route_algorithm_method(user_locations)
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
