from flask import Flask

app = Flask("TravelFast")

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/login/')
def test():
    return "Login Page will go here"
