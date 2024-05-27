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


@app.route("/plane/<string:plane_id>", methods=["GET", "POST"])
def plane(plane_id):
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    if request.method == "POST":
        rating = request.form.get("rating")
        if rating:
            rating = int(rating)
            cursor.execute("SELECT * FROM popular WHERE pid=?", (plane_id,))
            result = cursor.fetchone()
            if result:
                cursor.execute("""
                    UPDATE popular
                    SET ratings = ratings + ?, totalratings = totalratings + 1
                    WHERE pid = ?
                """, (rating, plane_id))
            else:
                cursor.execute("""
                    INSERT INTO popular (pid, ratings, totalratings)
                    VALUES (?, ?, 1)
                """, (plane_id, rating))
            connection.commit()
    cursor.execute("SELECT * FROM Plane WHERE id = ?", (plane_id,))
    plane = cursor.fetchone()
    cursor.execute("SELECT opened FROM popular WHERE pid = ?", (plane_id,))
    opened = cursor.fetchone()
    if opened:
        opened = opened[0] + 1
        cursor.execute("UPDATE popular SET opened = ? WHERE pid = ?;", (opened, plane_id))
        connection.commit()
    connection.close()
    if plane:
        return render_template('plane.html', planename=plane[1], planedesc=plane[2], planeimg=plane[3])
    else:
        return "Plane not found", 404



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


@app.route("/engine/<string:engine_id>", methods=["GET", "POST"])
def engine(engine_id):
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    if request.method == "POST":
        rating = request.form.get("rating")
        if rating:
            rating = int(rating)
            cursor.execute("SELECT * FROM popular WHERE eid=?", (engine_id,))
            result = cursor.fetchone()
            if result:
                cursor.execute("""
                    UPDATE popular
                    SET ratings = ratings + ?, totalratings = totalratings + 1
                    WHERE eid = ?
                """, (rating, engine_id))
            else:
                cursor.execute("""
                    INSERT INTO popular (eid, ratings, totalratings)
                    VALUES (?, ?, 1)
                """, (engine_id, rating))
            connection.commit()
    cursor.execute("SELECT * FROM Engine WHERE id = ?", (engine_id,))
    engine = cursor.fetchone()
    cursor.execute("SELECT opened FROM popular WHERE eid = ?", (engine_id,))
    opened = cursor.fetchone()
    if opened:
        opened = opened[0] + 1
        cursor.execute("UPDATE popular SET opened = ? WHERE eid = ?;", (opened, engine_id))
        connection.commit()
    connection.close()
    if engine:
        return render_template('engine.html', enginename=engine[1], enginedesc=engine[2], engineimg=engine[3])
    else:
        return "Engine not found", 404



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
    elif dir == "down":
        for i in range(1, lines + 1):
            actualLines.append(" "*(-1 + i) + "*"*(lines - i) + "*" + "*"*(lines - i))
    elif dir == "left":
        for i in range(1, lines + 1):
            actualLines.append(" "*(lines-i) + "*"*(i-1) + "*")
        for i in range(1, lines + 1):
            actualLines.append(" "*(i) + "*"*(lines - i))
    elif dir == "right":
        for i in range(1, lines + 1):
            actualLines.append("*" + "*"*(i-1))
        for i in range(1, lines + 1):
            actualLines.append("*"*(lines - i))
    elif dir == "diamond":
        for i in range(1, lines + 1):
            actualLines.append(" "*(lines-i) + "*"*(i-1) + "*" + "*"*(i-1))
        for i in range(1, lines + 1):
            actualLines.append(" "*(i) + "*"*(lines - i) + "*"*(lines - i - 1))
    elif dir == "sand":
        for i in range(1, lines + 1):
            actualLines.append(" "*(-1 + i) + "*"*(lines - i) + "*" + "*"*(lines - i))
        for i in range(1, lines + 1):
            actualLines.append(" "*(lines-i) + "*"*(i-1) + "*" + "*"*(i-1))
    else:
        for i in range(1, lines + 1):
            actualLines.append(" "*(lines-i) + "*"*(i-1) + "*" + "*"*(i-1))
    return render_template("triangle.html", triangle=actualLines)


@app.route("/asciiart/<string:letters>/")
def asciiArt(letters):
    asciiLeters1 = [["q", " ██████╗ "], ["w", "██╗    ██╗"]]
    asciiLeters2 = [["q", "██╔═══██╗"], ["w", "██║    ██║"]]
    asciiLeters3 = [["q", "██║   ██║"], ["w", "██║ █╗ ██║"]]
    asciiLeters4 = [["q", "██║▄▄ ██║"], ["w", "██║███╗██║"]]
    asciiLeters5 = [["q", "╚██████╔╝"], ["w", "╚███╔███╔╝"]]
    asciiLeters6 = [["q", " ╚══▀▀═╝ "], ["w", " ╚══╝╚══╝ "]]
    ascii1 = []
    ascii2 = []
    ascii3 = []
    ascii4 = []
    ascii5 = []
    ascii6 = []
    for i in letters:
        for letter in asciiLeters1:
            if letter[0] == i:
                ascii1.append(letter[1])
        for letter in asciiLeters2:
            if letter[0] == i:
                ascii2.append(letter[1])
        for letter in asciiLeters3:
            if letter[0] == i:
                ascii3.append(letter[1])
        for letter in asciiLeters4:
            if letter[0] == i:
                ascii4.append(letter[1])
        for letter in asciiLeters5:
            if letter[0] == i:
                ascii5.append(letter[1])
        for letter in asciiLeters6:
            if letter[0] == i:
                ascii6.append(letter[1])
    print(asciiLeters1, asciiLeters2, asciiLeters3, asciiLeters4, asciiLeters5, asciiLeters6)
    return render_template("asciiart.html", asciiart=[ascii1, ascii2, ascii3, ascii4, ascii5, ascii6])

if __name__ == "__main__":
    app.run(debug=True)  # live updates code when building a website