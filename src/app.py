from flask import Flask, request, render_template, redirect, url_for, session
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
app.config['MYSQL_HOST'] = 'pythonanywhere' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'TravelFastDB'

app.config.from_object(__name__)

Session(app)
mysql = MySQL(app)


@app.route('/')
def redirect_to_login():
    return render_template("login.html")

user_credentials = {"Bob": "bobiscool", "John": "password"} # Just a placeholder for the real database system for now

user_locations = [] # Just a placeholder for the real database system for now

# took inspiration for mysql functionality from https://www.geeksforgeeks.org/profile-application-using-python-flask-and-mysql/

@app.route('/login/', methods=["POST", "GET"])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form["username"]
        password = request.form["password"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM users WHERE username = % s AND password = % s', (username, password)
        )
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
    
@app.route('/create_account/', methods=["POST", "GET"])
def create_account():
    try:
        username = request.form["username"]
        password = request.form["password"]
    except:
        return render_template("account_create.html")
    if username in user_credentials:
        return render_template("account_create.html", return_info = "This username already exists!")
    else:
        user_credentials[username] = password
        return render_template("account_create.html", return_info = "Account succesfully created!")
    
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