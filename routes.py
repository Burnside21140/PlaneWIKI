from flask import Flask, render_template, request, redirect, url_for

import sqlite3


app = Flask(__name__)


def databaseOpen(): # Connecting to the database for SQL querys
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    return connection,cursor


@app.route("/", methods=["GET"]) # Page route and form methods
def home(): # Page function
    sort_option = request.args.get("Sort", "new") # Fetching the desired sort method to fetch the planes and engines in the corresponding order
    connection, cursor = databaseOpen() # Connecting to the database
    if sort_option == "new": # Returning all planes and engines in the order of newest to oldest
        query = """
            SELECT id, name, description, picture, 'plane' AS type, id AS sort_value FROM Plane
            UNION ALL
            SELECT id, name, description, picture, 'engine' AS type, id AS sort_value FROM Engine
            ORDER BY sort_value DESC
        """
    elif sort_option == "old": # Returning all planes and engines in the order of oldest to newest
        query = """
            SELECT id, name, description, picture, 'plane' AS type, id AS sort_value FROM Plane
            UNION ALL
            SELECT id, name, description, picture, 'engine' AS type, id AS sort_value FROM Engine
            ORDER BY sort_value ASC
        """
    elif sort_option == "mostViews": # Returning all planes and engines in the order of most views
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
    elif sort_option == "leastViews": # Returning all planes and engines in the order of least views
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
    elif sort_option == "A-Z": # Returning all planes and engines in the order of A-Z
        query = """
            SELECT id, name, description, picture, 'plane' AS type, name AS sort_value FROM Plane
            UNION ALL
            SELECT id, name, description, picture, 'engine' AS type, name AS sort_value FROM Engine
            ORDER BY sort_value COLLATE NOCASE ASC
        """
    elif sort_option == "Z-A": # Returning all planes and engines in the order of Z-A
        query = """
            SELECT id, name, description, picture, 'plane' AS type, name AS sort_value FROM Plane
            UNION ALL
            SELECT id, name, description, picture, 'engine' AS type, name AS sort_value FROM Engine
            ORDER BY sort_value COLLATE NOCASE DESC
        """
    elif sort_option == "bestRatings":
        query = """
            SELECT p.id, p.name, p.description, p.picture, 'plane' AS type,
                   (pop.ratings * 1.0 / pop.totalratings) AS sort_value
            FROM Plane p JOIN popular pop ON p.id = pop.pid
            UNION ALL
            SELECT e.id, e.name, e.description, e.picture, 'engine' AS type,
                   (pop.ratings * 1.0 / pop.totalratings) AS sort_value
            FROM Engine e JOIN popular pop ON e.id = pop.eid
            ORDER BY sort_value DESC
        """
    elif sort_option == "worstRatings":
        query = """
            SELECT p.id, p.name, p.description, p.picture, 'plane' AS type,
                   (pop.ratings * 1.0 / pop.totalratings) AS sort_value
            FROM Plane p JOIN popular pop ON p.id = pop.pid
            UNION ALL
            SELECT e.id, e.name, e.description, e.picture, 'engine' AS type,
                   (pop.ratings * 1.0 / pop.totalratings) AS sort_value
            FROM Engine e JOIN popular pop ON e.id = pop.eid
            ORDER BY sort_value ASC
        """
    elif sort_option == "mostRatings":
        query = """
            SELECT p.id, p.name, p.description, p.picture, 'plane' AS type, pop.totalratings AS sort_value
            FROM Plane p JOIN popular pop ON p.id = pop.pid
            UNION ALL
            SELECT e.id, e.name, e.description, e.picture, 'engine' AS type, pop.totalratings AS sort_value
            FROM Engine e JOIN popular pop ON e.id = pop.eid
            ORDER BY sort_value DESC
        """
    elif sort_option == "leastRatings":
        query = """
            SELECT p.id, p.name, p.description, p.picture, 'plane' AS type, pop.totalratings AS sort_value
            FROM Plane p JOIN popular pop ON p.id = pop.pid
            UNION ALL
            SELECT e.id, e.name, e.description, e.picture, 'engine' AS type, pop.totalratings AS sort_value
            FROM Engine e JOIN popular pop ON e.id = pop.eid
            ORDER BY sort_value ASC
        """
    else:  # Incase of no option selected, returning all planes and engines in the order of newest to oldest
        query = """
            SELECT id, name, description, picture, 'plane' AS type, id AS sort_value FROM Plane
            UNION ALL
            SELECT id, name, description, picture, 'engine' AS type, id AS sort_value FROM Engine
        """
    cursor.execute(query)
    pages = cursor.fetchall()
    connection.close()
    return render_template("home.html", pages=pages, sort_option=sort_option) # Rendering the html page with pages as both the planes and engines, sort_option to get the html to show which sort option is currently selected


@app.route("/planes") # Page route
def planes(): # Page function
    sort_option = request.args.get("Sort", "new") # Fetching the desired sort method to fetch the planes and engines in the corresponding order
    connection, cursor = databaseOpen() # Connecting to the database
    if sort_option == "new": # Returning the planes in order of newest
        cursor.execute("SELECT * FROM Plane ORDER BY id DESC")
    elif sort_option == "old": # Returning the planes in order of oldest
        cursor.execute("SELECT * FROM Plane ORDER BY id ASC")
    elif sort_option == "mostViews": # Returning the planes in order of most views
        cursor.execute("""
            SELECT Plane.id, Plane.name, Plane.description, Plane.picture
            FROM Plane
            LEFT JOIN popular ON Plane.id = popular.pid
            ORDER BY popular.opened DESC
        """)
    elif sort_option == "leastViews": # Returning the planes in order of least views
        cursor.execute("""
            SELECT Plane.id, Plane.name, Plane.description, Plane.picture
            FROM Plane
            LEFT JOIN popular ON Plane.id = popular.pid
            ORDER BY popular.opened ASC
        """)
    elif sort_option == "A-Z": # Returning the planes in order of A-Z
        cursor.execute("SELECT * FROM Plane ORDER BY name ASC")
    elif sort_option == "Z-A": # Returning the planes in order of Z-A
        cursor.execute("SELECT * FROM Plane ORDER BY name DESC")
    elif sort_option == "bestRatings":
        cursor.execute("""
            SELECT p.id, p.name, p.description, p.picture,
                   (pop.ratings * 1.0 / pop.totalratings) AS avg_rating
            FROM Plane p JOIN popular pop ON p.id = pop.pid
            ORDER BY avg_rating DESC
        """)
    elif sort_option == "worstRatings":
        cursor.execute("""
            SELECT p.id, p.name, p.description, p.picture,
                   (pop.ratings * 1.0 / pop.totalratings) AS avg_rating
            FROM Plane p JOIN popular pop ON p.id = pop.pid
            ORDER BY avg_rating ASC
        """)
    elif sort_option == "mostRatings":
        cursor.execute("""
            SELECT p.id, p.name, p.description, p.picture
            FROM Plane p JOIN popular pop ON p.id = pop.pid
            ORDER BY pop.totalratings DESC
        """)
    elif sort_option == "leastRatings":
        cursor.execute("""
            SELECT p.id, p.name, p.description, p.picture
            FROM Plane p JOIN popular pop ON p.id = pop.pid
            ORDER BY pop.totalratings ASC
        """)
    else: # Incase of no order option selected return all planes by newest
        cursor.execute("SELECT * FROM Plane")
    planes = cursor.fetchall()
    connection.close()
    planelist = [] # What information we'll give to the html page
    for plane in planes: # Going through the SQL results to get the information we want
        item = [plane[0], plane[1], plane[2], plane[3]] # Selecting the ID, Name, Discription, and Image respectively as a nested list
        planelist.append(item)
    return render_template("planes.html", planes=planelist, sort_option=sort_option) # Rendering the HTML page with planes as the different planes with the required data and sort_option for the html to show which sort option is selected


@app.route("/plane/<string:plane_id>", methods=["GET", "POST"]) # Page route with the desired methods
def plane(plane_id): # Page function
    connection, cursor = databaseOpen() # Connecting to the database
    if request.method == "POST": # Receiving the rating given
        rating = request.form.get("rating") # Receiving the value of the rating
        if rating:
            rating = int(rating)
            cursor.execute("""
                UPDATE popular
                SET ratings = ratings + ?, totalratings = totalratings + 1
                WHERE pid = ?
            """, (rating, plane_id)) # Adding the value of the rating and the amount of ratings to the plane in the popular table
            connection.commit()
    cursor.execute("SELECT * FROM Plane WHERE id = ?", (plane_id,)) # Fetching the plane's information for the planes table
    plane = cursor.fetchone()
    if plane: # Checking that the plane does in fact exist
        cursor.execute("SELECT opened FROM popular WHERE pid = ?", (plane_id,)) # Fetching how many times the plane's page has been opened
        opened = cursor.fetchone()
        if opened: # Checking if the plane exists in the popular table and increasing the amount of times the page has been opened
            opened = opened[0] + 1
            cursor.execute("UPDATE popular SET opened = ? WHERE pid = ?;", (opened, plane_id))
        else: # If the plane does not exist in the popular table add the plane into the popular table with its 1 view (times opened)
                cursor.execute("""
                    INSERT INTO popular (pid, opened)
                    VALUES (?, 1)
                """, (plane_id,))
        connection.commit()
        connection.close()
        return render_template('plane.html', planename=plane[1], planedesc=plane[2], planeimg=plane[3])
    else: # If the plane does not exist return a 404 error
        return "Plane not found", 404



@app.route("/engines", methods=["GET"]) # Page route and form methods
def engines(): # Page function
    sort_option = request.args.get("Sort", "new") # Fetching the sorting option
    connection, cursor = databaseOpen() # Connecting to the database
    if sort_option == "new": # Fetching the engines sort by newest
        cursor.execute("SELECT * FROM Engine ORDER BY id DESC")
    elif sort_option == "old": # Fetching the engines sort by oldest
        cursor.execute("SELECT * FROM Engine ORDER BY id ASC")
    elif sort_option == "mostViews": # Fetching the engines sort by most views
        cursor.execute("""
            SELECT Engine.id, Engine.name, Engine.description, Engine.picture
            FROM Engine
            LEFT JOIN popular ON Engine.id = popular.eid
            ORDER BY popular.opened DESC
        """)
    elif sort_option == "leastViews": # Fetching the engines sort by least views
        cursor.execute("""
            SELECT Engine.id, Engine.name, Engine.description, Engine.picture
            FROM Engine
            LEFT JOIN popular ON Engine.id = popular.eid
            ORDER BY popular.opened ASC
        """)
    elif sort_option == "A-Z": # Fetching the engines sort by A-Z
        cursor.execute("SELECT * FROM Engine ORDER BY name ASC")
    elif sort_option == "Z-A": # Fetching the engines sort by Z-A
        cursor.execute("SELECT * FROM Engine ORDER BY name DESC")
    elif sort_option == "bestRatings":
        cursor.execute("""
            SELECT e.id, e.name, e.description, e.picture,
                   (pop.ratings * 1.0 / pop.totalratings) AS avg_rating
            FROM Engine e JOIN popular pop ON e.id = pop.eid
            ORDER BY avg_rating DESC
        """)
    elif sort_option == "worstRatings":
        cursor.execute("""
            SELECT e.id, e.name, e.description, e.picture,
                   (pop.ratings * 1.0 / pop.totalratings) AS avg_rating
            FROM Engine e JOIN popular pop ON e.id = pop.eid
            ORDER BY avg_rating ASC
        """)
    elif sort_option == "mostRatings":
        cursor.execute("""
            SELECT e.id, e.name, e.description, e.picture
            FROM Engine e JOIN popular pop ON e.id = pop.eid
            ORDER BY pop.totalratings DESC
        """)
    elif sort_option == "leastRatings":
        cursor.execute("""
            SELECT e.id, e.name, e.description, e.picture
            FROM Engine e JOIN popular pop ON e.id = pop.eid
            ORDER BY pop.totalratings ASC
        """)
    else: # Incase of no search option selected fetch engines in order of newest
        cursor.execute("SELECT * FROM Engine")
    engines = cursor.fetchall()
    connection.close()
    enginelist = [] # The list data that'll be passing to the HTML
    for engine in engines: 
        item = [engine[0], engine[1], engine[2], engine[3]] # Adding the ID, Name, Description, and Picture of the engine as a nested list to enginelist
        enginelist.append(item)
    return render_template("engines.html", engines=enginelist, sort_option=sort_option) # Rendering the HTML page with engines as the different engines with the required data and sort_option for the html to show which sort option is selected


@app.route("/engine/<string:engine_id>", methods=["GET", "POST"]) # Page route and form methods
def engine(engine_id): # Page function
    connection, cursor = databaseOpen() # Connecting to the database
    if request.method == "POST":
        rating = request.form.get("rating") # Getting the rating given by the user
        if rating:
            rating = int(rating)
            cursor.execute("""
                UPDATE popular
                SET ratings = ratings + ?, totalratings = totalratings + 1
                WHERE eid = ?
            """, (rating, engine_id))
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



@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        # Get form data
        plane_engine = request.form.get("PlaneEngine")
        name = request.form.get("name")
        description = request.form.get("description")
        password = request.form.get("password")
        # Insert into the database
        connection, cursor = databaseOpen()  # Connecting to the database
        if plane_engine == "plane":
            cursor.execute("INSERT INTO plane (name, description, password) VALUES (?, ?, ?)",
                           (name, description, password))
            connection.commit()
            cursor.execute("SELECT id FROM plane WHERE name = ? AND description = ? AND password = ?",
                           (name, description, password))
            id = cursor.fetchone()
            cursor.execute("INSERT INTO popular (pid, opened, ratings, totalratings) VALUES (?, 0, 0, 0)",
                           (id[0],))
            connection.commit()
        elif plane_engine == "engine":
            cursor.execute("INSERT INTO engine (name, description, password) VALUES (?, ?, ?)",
                           (name, description, password))
            connection.commit()
            cursor.execute("SELECT id FROM engine WHERE name = ? AND description = ? AND password = ?",
                           (name, description, password))
            id = cursor.fetchone()
            cursor.execute("INSERT INTO popular (eid, opened, ratings, totalratings) VALUES (?, 0, 0, 0)",
                           (id[0],))
            connection.commit()
        connection.close()
        return render_template("created.html")
    else:
        return render_template("create.html")


# Easter egg code
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


# Easter egg code
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