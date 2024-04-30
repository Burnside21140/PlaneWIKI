from flask import Flask, render_template

import sqlite3


app = Flask(__name__)


@app.route("/")  # ROUTE DECORATOR
def home():     # ROUTE FUNCTION
    return render_template("home.html")


@app.route("/planes")  # ROUTE DECORATOR
def planes():     # ROUTE FUNCTION
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Plane")
    planes = cursor.fetchall()
    connection.close()
    planelist = []
    for i in planes:
        item = [i[0], i[1], i[2], i[3]]
        planelist.append(item)
    return render_template("planes.html", planes=planelist)


@app.route("/engines")  # ROUTE DECORATOR
def engines():     # ROUTE FUNCTION
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Engine")
    engines = cursor.fetchall()
    connection.close()
    enginelist = []
    for i in engines:
        item = [i[0], i[1], i[2], i[3]]
        enginelist.append(item)
    return render_template("engines.html", engines=enginelist)


@app.route("/create")  # ROUTE DECORATOR
def create():     # ROUTE FUNCTION
    return render_template("create.html")


if __name__ == "__main__":
    app.run(debug=True)  # live updates code when building a website
