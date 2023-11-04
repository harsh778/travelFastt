from flask import Flask, request, render_template, redirect, url_for, session, make_response, jsonify
from flask_session import Session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import secrets
from datetime import timedelta

import algorithms.bruteforce as BruteForceAlgorithm

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
            
    # try:
    #     username = request.form["username"]
    #     password = request.form["password"]
    # except:
    #     return render_template("login.html")
    # if username not in user_credentials:
    #     return render_template("login.html", return_info = "Username not found!")
    # elif user_credentials[username] != password:
    #     return render_template("login.html", return_info = "Incorrect password for this account! Please try again.")
    # else:
    #     return render_template("home.html", user = username)
    
    
    
# ------------ LOGOUT --------------
# need to research more about sessions and how we are keeping track of the user in our code
@app.route('/logout/')
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
    
    
    # try:
    #     username = request.form["username"]
    #     password = request.form["password"]
    # except:
    #     return render_template("account_create.html")
    # if username in user_credentials:
    #     return render_template("account_create.html", return_info = "This username already exists!")
    # else:
    #     user_credentials[username] = password
    #     return render_template("account_create.html", return_info = "Account succesfully created!")
    
    
# ------------ SAVE USER'S ROUTES --------------
# -Stores a user's route in the database
# -This route has no method for now
@app.route('/store_user_route/')
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




@app.route('/temp_bypass_to_map/', methods=["POST", "GET"])
def to_map():
    return render_template("home.html", user = "TEMP", return_info = "TEMP")


@app.route('/temp_bypass_to_route_finder/', methods=["POST", "GET"])
def to_route_finder():
    return render_template("route_finder.html", return_info = "Your list of added locations will show up here!")


@app.route('/add_location/', methods=["POST", "GET"])
def add_location():
    try:
        latitude = float(request.form["latitude"])
        longitude = float(request.form["longitude"])
    except:
        return render_template("route_finder.html", return_info = "Unable to add most recent location. Did you input numbers to both fields?")
    
    
    user_locations.append([latitude, longitude])
    added_duplicate = False
    formatted_locations_string = ""
    for i, location in enumerate(user_locations):
        if location[0] == latitude and location[1] == longitude and i != len(user_locations) - 1: # User tried to add duplicate location, ignored by skipping it entirely
            added_duplicate = True
            continue
        formatted_locations_string += f"Latitude: {location[0]}, Longitude: {location[1]} "
    if added_duplicate:
        user_locations.pop() # Remove the duplicate location
    return render_template("route_finder.html", return_info = formatted_locations_string)


@app.route('/clear_route_locations/', methods=["POST", "GET"])
def clear_locations():
    user_locations.clear()
    return render_template("route_finder.html", return_info = "Route Locations Cleared.")


@app.route('/calculate_route/', methods=["POST", "GET"])
def calculate_route():
    route = BruteForceAlgorithm.best_route(user_locations)
    formatted_route_string = "Full Route --> "
    for i, location in enumerate(route):
        formatted_route_string += f"Stop {i + 1}: Latitude {location[0]}, Longitude {location[1]}. "
    return render_template("route_finder.html", return_info = formatted_route_string)

@app.route('/return_route/', methods=["POST", "GET"])
def return_route():
    unused_request = request.get_json(force=True) # Don't actually need anything from the request but need to 'process' it
    route = BruteForceAlgorithm.best_route(user_locations) # Later this should just be a fetch from the database instead of recalculating every time
    response = make_response(jsonify(route))
    return response