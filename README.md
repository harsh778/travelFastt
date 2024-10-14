# TravelFast

## What is TravelFast?

TravelFast is a web app designed for people with many destinations, like truck drivers, Uber Eats delivery, or even tourists. 
TravelFast will optimize a route for users to take between their many stops to reduce the time they have to travel.

Our app also includes an educational component that allows users to compare different path calculation algorithms and see how the paths differ.

For an in-depth look at our app, see our project proposal [here](https://docs.google.com/document/d/1xIrM3k-8SyTNoDECC_0MIYr3OR31FlxIJEoNck5NrKs/edit?usp=sharing).


## TravelFast Architecture:

![](https://github.com/CS222-UIUC-FA23/group-project-team100/blob/7778ee107278189dea80f2300021e30dbfb3442f/TravelFast%20Architecture.png)

## TravelFast Developers:
- **Aydin Ali**: Designed the whole frontend UI with Javascript handling for map display with coordinates and route calculation methods in Flask Server
- **Mike Koziol**: Implemented Flask Server with sessions and MySQL Database functionality
- **Ajitesh Dasaratha**: Made different algorithms to calculate routes
- **Harsh Singhal**: Researched algorithms and explained workings to Ajitesh for implementation purposes.


## Getting Started With Our App:

As of now, our app is not deployed on the cloud or a public server, so it will need to be locally hosted on a personal computer.

First, initialize the MySQL Database using this [link](https://docs.google.com/document/d/1Ig5B0PzZk6yhPIR0x4AIRQrU_zTCsEc6GDBuWw0Qm9U/edit?usp=sharing).

For the Flask Server, we recommend using a Python 3 virtual environment with package installation enabled. [Here](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) 
is an in-depth link for how to create a Python virtual environment with packages for both Mac and Windows.

Once you have a venv, you will need to pip install the following packages:
flask, flask_session, flask_mysqldb, secrets, re, MySQLdb.

Once all installations are complete, your venv is running, and you are in the parent directory, you may run:
```
python -m flask --app src/app.py run
```
To run the Flask Server and start using our web app.
