from flask import Flask, render_template, request, redirect, url_for

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


@app.route("/plane/<string:plane_id>")
def plane(plane_id):
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Plane where id = ?", (plane_id,))
    plane = cursor.fetchone()
    connection.close()
    return render_template('plane.html', planename=plane[1], planedesc=plane[2], planeimg=plane[3])


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


@app.route("/engine/<string:engine_id>")
def engine(engine_id):
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Engine where id = ?", (engine_id,))
    engine = cursor.fetchone()
    connection.close()
    return render_template('engine.html', enginename=engine[1], enginedesc=engine[2], engineimg=engine[3])


# Route for the create page
@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        # Get form data
        plane_engine = request.form["PlaneEngine"]
        print(plane_engine)
        name = request.form["name"]
        description = request.form["description"]
        password = request.form["password"]

        # Insert into the database
        conn = sqlite3.connect("your_database.db")
        cursor = conn.cursor()
        if plane_engine == "plane":
            cursor.execute("INSERT INTO plane (name, description, password) VALUES (?, ?, ?)",
                       (name, description, password))
        if plane_engine == "engine":
            cursor.execute("INSERT INTO engine (name, description, password) VALUES (?, ?, ?)",
                       (name, description, password))
        conn.commit()
        conn.close()

        return redirect(url_for("success"))  # Redirect to a success page or another route
    else:
        return render_template("create.html")

# Route for the success page
@app.route("/success")
def success():
    return "Form submitted successfully!"


if __name__ == "__main__":
    app.run(debug=True)  # live updates code when building a website
