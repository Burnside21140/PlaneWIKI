from flask import Flask, render_template, request, redirect, url_for

import sqlite3


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    sort_option = request.args.get("Sort", "new")
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    if sort_option == "new":
        query = """
            SELECT id, name, description, picture, 'plane' AS type, id AS sort_value FROM Plane
            UNION ALL
            SELECT id, name, description, picture, 'engine' AS type, id AS sort_value FROM Engine
            ORDER BY sort_value DESC
        """
    elif sort_option == "old":
        query = """
            SELECT id, name, description, picture, 'plane' AS type, id AS sort_value FROM Plane
            UNION ALL
            SELECT id, name, description, picture, 'engine' AS type, id AS sort_value FROM Engine
            ORDER BY sort_value ASC
        """
    elif sort_option == "mostViews":
        query = """
            SELECT Plane.id, Plane.name, Plane.description, Plane.picture, 'plane' AS type, IFNULL(popular.opened, 0) AS sort_value
            FROM Plane
            LEFT JOIN popular ON Plane.id = popular.pid
            UNION ALL
            SELECT Engine.id, Engine.name, Engine.description, Engine.picture, 'engine' AS type, IFNULL(popular.opened, 0) AS sort_value
            FROM Engine
            LEFT JOIN popular ON Engine.id = popular.eid
            ORDER BY sort_value DESC
        """
    elif sort_option == "leastViews":
        query = """
            SELECT Plane.id, Plane.name, Plane.description, Plane.picture, 'plane' AS type, IFNULL(popular.opened, 0) AS sort_value
            FROM Plane
            LEFT JOIN popular ON Plane.id = popular.pid
            UNION ALL
            SELECT Engine.id, Engine.name, Engine.description, Engine.picture, 'engine' AS type, IFNULL(popular.opened, 0) AS sort_value
            FROM Engine
            LEFT JOIN popular ON Engine.id = popular.eid
            ORDER BY sort_value ASC
        """
    elif sort_option == "A-Z":
        query = """
            SELECT id, name, description, picture, 'plane' AS type, name AS sort_value FROM Plane
            UNION ALL
            SELECT id, name, description, picture, 'engine' AS type, name AS sort_value FROM Engine
            ORDER BY sort_value COLLATE NOCASE ASC
        """
    elif sort_option == "Z-A":
        query = """
            SELECT id, name, description, picture, 'plane' AS type, name AS sort_value FROM Plane
            UNION ALL
            SELECT id, name, description, picture, 'engine' AS type, name AS sort_value FROM Engine
            ORDER BY sort_value COLLATE NOCASE DESC
        """
    else:
        query = """
            SELECT id, name, description, picture, 'plane' AS type, id AS sort_value FROM Plane
            UNION ALL
            SELECT id, name, description, picture, 'engine' AS type, id AS sort_value FROM Engine
        """
    cursor.execute(query)
    pages = cursor.fetchall()
    connection.close()
    return render_template("home.html", pages=pages, sort_option=sort_option)


@app.route("/planes")  # ROUTE DECORATOR
def planes():     # ROUTE FUNCTION
    sort_option = request.args.get("Sort", "new")
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    if sort_option == "new":
        cursor.execute("SELECT * FROM Plane ORDER BY id DESC")
    elif sort_option == "old":
        cursor.execute("SELECT * FROM Plane ORDER BY id ASC")
    elif sort_option == "mostViews":
        cursor.execute("""
            SELECT Plane.id, Plane.name, Plane.description, Plane.picture
            FROM Plane
            LEFT JOIN popular ON Plane.id = popular.pid
            ORDER BY popular.opened DESC
        """)
    elif sort_option == "leastViews":
        cursor.execute("""
            SELECT Plane.id, Plane.name, Plane.description, Plane.picture
            FROM Plane
            LEFT JOIN popular ON Plane.id = popular.pid
            ORDER BY popular.opened ASC
        """)
    elif sort_option == "A-Z":
        cursor.execute("SELECT * FROM Plane ORDER BY name ASC")
    elif sort_option == "Z-A":
        cursor.execute("SELECT * FROM Plane ORDER BY name DESC")
    else:
        cursor.execute("SELECT * FROM Plane")
    planes = cursor.fetchall()
    connection.close()
    planelist = []
    for plane in planes:
        item = [plane[0], plane[1], plane[2], plane[3]]
        planelist.append(item)
    return render_template("planes.html", planes=planelist, sort_option=sort_option)


@app.route("/plane/<string:plane_id>")
def plane(plane_id):
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Plane where id = ?", (plane_id,))
    plane = cursor.fetchone()
    cursor.execute("SELECT opened FROM popular WHERE pid = ?", (plane_id,))
    opened = cursor.fetchone()
    opened = opened[0] + 1
    cursor.execute("UPDATE popular SET opened = ? WHERE pid = ?;",
                   (opened, plane_id,))
    connection.commit()
    connection.close()
    return render_template('plane.html', planename=plane[1], planedesc=plane[2], planeimg=plane[3])


@app.route("/engines", methods=["GET"])
def engines():
    sort_option = request.args.get("Sort", "new")
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    if sort_option == "new":
        cursor.execute("SELECT * FROM Engine ORDER BY id DESC")
    elif sort_option == "old":
        cursor.execute("SELECT * FROM Engine ORDER BY id ASC")
    elif sort_option == "mostViews":
        cursor.execute("""
            SELECT Engine.id, Engine.name, Engine.description, Engine.picture
            FROM Engine
            LEFT JOIN popular ON Engine.id = popular.eid
            ORDER BY popular.opened DESC
        """)
    elif sort_option == "leastViews":
        cursor.execute("""
            SELECT Engine.id, Engine.name, Engine.description, Engine.picture
            FROM Engine
            LEFT JOIN popular ON Engine.id = popular.eid
            ORDER BY popular.opened ASC
        """)
    elif sort_option == "A-Z":
        cursor.execute("SELECT * FROM Engine ORDER BY name ASC")
    elif sort_option == "Z-A":
        cursor.execute("SELECT * FROM Engine ORDER BY name DESC")
    else:
        cursor.execute("SELECT * FROM Engine")
    engines = cursor.fetchall()
    connection.close()
    enginelist = []
    for engine in engines:
        item = [engine[0], engine[1], engine[2], engine[3]]
        enginelist.append(item)
    return render_template("engines.html", engines=enginelist, sort_option=sort_option)


@app.route("/engine/<string:engine_id>")
def engine(engine_id):
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Engine where id = ?", (engine_id,))
    engine = cursor.fetchone()
    cursor.execute("SELECT opened FROM popular WHERE eid = ?", (engine_id,))
    opened = cursor.fetchone()
    opened = opened[0] + 1
    cursor.execute("UPDATE popular SET opened = ? WHERE eid = ?;",
                   (opened, engine_id,))
    connection.commit()
    connection.close()
    return render_template('engine.html', enginename=engine[1], enginedesc=engine[2], engineimg=engine[3])


# Route for the create page
@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        # Get form data
        plane_engine = request.form["PlaneEngine"]
        name = request.form["name"]
        description = request.form["description"]
        password = request.form["password"]

        # Insert into the database
        connection = sqlite3.connect('planeWIKIDB.db')
        cursor = connection.cursor()
        if plane_engine == "plane":
            cursor.execute("INSERT INTO plane (name, description, password) VALUES (?, ?, ?)",
                           (name, description, password))
            connection.commit()
            cursor.execute(
                "SELECT id FROM plane where name = ? AND description = ? AND password = ?", (name, description, password))
            id = cursor.fetchone()
            cursor.execute("INSERT INTO popular (pid, opened, ratings, totalratings) VALUES (?, 0, 0, 0)",
                           (id[0],))
            connection.commit()
        if plane_engine == "engine":
            cursor.execute("INSERT INTO engine (name, description, password) VALUES (?, ?, ?)",
                           (name, description, password))
            connection.commit()
            cursor.execute(
                "SELECT id FROM engine where name = ? AND description = ? AND password = ?", (name, description, password))
            id = cursor.fetchone()
            cursor.execute("INSERT INTO popular (eid, opened, ratings, totalratings) VALUES (?, 0, 0, 0)",
                           (id[0],))
            connection.commit()
        # Redirect to a success page or another route
        return render_template("created.html")
    else:
        return render_template("create.html")


# Route for the success page
@app.route("/success")
def success():
    return "Form submitted successfully!"


@app.route("/triangle/<string:lines>/<string:dir>")
def triangles(lines, dir):
    lines = int(lines)
    actualLines = []
    if lines <= 0:
        return render_template("triangle.html", triangle=["You need to put in a value greater then 0"])
    if dir == "up":
        for i in range(1, lines + 1):
            actualLines.append(" "*(lines-i) + "*"*(i-1) + "*" + "*"*(i-1))
    if dir == "down":
        for i in range(1, lines + 1):
            actualLines.append(" "*(-1 + i) + "*"*(lines - i) + "*" + "*"*(lines - i))
    if dir == "left":
        for i in range(1, lines + 1):
            actualLines.append(" "*(lines-i) + "*"*(i-1) + "*")
        for i in range(1, lines + 1):
            actualLines.append(" "*(i) + "*"*(lines - i))
    if dir == "right":
        for i in range(1, lines + 1):
            actualLines.append("*" + "*"*(i-1))
        for i in range(1, lines + 1):
            actualLines.append("*"*(lines - i))
    if dir == "diamond":
        for i in range(1, lines + 1):
            actualLines.append(" "*(lines-i) + "*"*(i-1) + "*" + "*"*(i-1))
        for i in range(1, lines + 1):
            actualLines.append(" "*(i) + "*"*(lines - i) + "*"*(lines - i - 1))

    return render_template("triangle.html", triangle=actualLines)


if __name__ == "__main__":
    app.run(debug=True)  # live updates code when building a website