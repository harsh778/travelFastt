from flask import Flask, request, render_template

app = Flask("TravelFast")

@app.route('/')
def redirect_to_login():
    return render_template("login.html")

user_credentials = {"Bob": "bobiscool", "John": "password"} # Just a placeholder for the real database system for now

@app.route('/login/', methods=["POST", "GET"])
def login():
    try:
        username = request.form["username"]
        password = request.form["password"]
    except:
        return render_template("login.html")
    if username not in user_credentials:
        return render_template("login.html", return_info = "Username not found!")
    elif user_credentials[username] != password:
        return render_template("login.html", return_info = "Incorrect password for this account! Please try again.")
    else:
        return render_template("home.html", user = username)
    
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