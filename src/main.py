from flask import Flask, request, render_template, redirect, url_for, session
from flask_session import Session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import secrets
from datetime import timedelta

app = Flask("TravelFast")


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

app.config.from_object("TravelFast")

Session(app)
mysql = MySQL(app)


@app.route('/')
def redirect_to_login():
    return render_template("login.html")

user_credentials = {"Bob": "bobiscool", "John": "password"} # Just a placeholder for the real database system for now

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
            return render_template('home.html', user = username, return_info = msg)
        else:
            msg = 'Incorrect username or password'
    return render_template('login.html', return_info = msg)
            
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