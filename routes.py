from flask import Flask, render_template, request, redirect, url_for, jsonify

import sqlite3

app = Flask(__name__)


def databaseOpen(): # Connecting to the database for SQL querys
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    return connection,cursor


def databaseSelect(page, sort): # Returns the desired query for the situation
    query = str()
    if page == "home":
        if sort == "new" or sort == "old":
            query = f"""
                SELECT id, name, description, picture, 'plane' AS type, id AS sort_value, IFNULL(ratings, 0) * 1.0 / IFNULL(totalratings, 1) AS avg_rating FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                UNION ALL
                SELECT id, name, description, picture, 'engine' AS type, id AS sort_value, IFNULL(ratings, 0) * 1.0 / IFNULL(totalratings, 1) AS avg_rating FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value {'DESC' if sort == 'new' else 'ASC'}
            """
        elif sort == "mostViews" or sort == "leastViews":
            query = f"""
                SELECT Plane.id, Plane.name, Plane.description, Plane.picture, 'plane' AS type, IFNULL(popular.opened, 0) AS sort_value, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                UNION ALL
                SELECT Engine.id, Engine.name, Engine.description, Engine.picture, 'engine' AS type, IFNULL(popular.opened, 0) AS sort_value, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value {'DESC' if sort == 'mostViews' else 'ASC'}
            """
        elif sort == "A-Z" or sort == "Z-A":
            query = f"""
                SELECT id, name, description, picture, 'plane' AS type, name AS sort_value, 
                IFNULL(ratings, 0) * 1.0 / IFNULL(totalratings, 1) AS avg_rating 
                FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                UNION ALL
                SELECT id, name, description, picture, 'engine' AS type, name AS sort_value, 
                IFNULL(ratings, 0) * 1.0 / IFNULL(totalratings, 1) AS avg_rating 
                FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value COLLATE NOCASE {'DESC' if sort == 'Z-A' else 'ASC'}
            """
        elif sort == "bestRatings" or sort == "worstRatings":
            query = f"""
                SELECT Plane.id, Plane.name, Plane.description, Plane.picture, 'plane' AS type, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS sort_value, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                UNION ALL
                SELECT Engine.id, Engine.name, Engine.description, Engine.picture, 'engine' AS type, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS sort_value, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value {'DESC' if sort == 'bestRatings' else 'ASC'}
            """
        elif sort == "mostRatings" or sort == "leastRatings":
            query = f"""
                SELECT Plane.id, Plane.name, Plane.description, Plane.picture, 'plane' AS type, IFNULL(popular.totalratings, 0) AS sort_value, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                UNION ALL
                SELECT Engine.id, Engine.name, Engine.description, Engine.picture, 'engine' AS type, IFNULL(popular.totalratings, 0) AS sort_value, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value {'DESC' if sort == 'mostRatings' else 'ASC'}
            """
        else:
            query = """
                SELECT id, name, description, picture, 'plane' AS type, id AS sort_value, IFNULL(ratings, 0) * 1.0 / IFNULL(totalratings, 1) AS avg_rating FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                UNION ALL
                SELECT id, name, description, picture, 'engine' AS type, id AS sort_value, IFNULL(ratings, 0) * 1.0 / IFNULL(totalratings, 1) AS avg_rating FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value DESC
            """
    elif page == "planes":
        if sort == "new" or sort == "old"  or sort == "A-Z" or sort == "Z-A":
            query = f"""
                SELECT Plane.*, IFNULL(ratings, 0) * 1.0 / IFNULL(totalratings, 1) AS avg_rating FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                ORDER BY {'Plane.id' if sort == 'new' or sort == "old" else 'Plane.name'} {"COLLATE NOCASE" if "-" in sort else ""} {'DESC' if sort == 'new' or sort == "Z-A" else 'ASC'} 
            """
        elif sort == "mostViews" or sort == "leastViews":
            query = f"""
                SELECT Plane.*, IFNULL(popular.opened, 0) AS sort_value, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                ORDER BY sort_value {'DESC' if sort == 'mostViews' else 'ASC'}
            """
        elif sort == "bestRatings" or sort == "worstRatings":
            query = f"""
                SELECT Plane.*, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS avg_rating FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                ORDER BY avg_rating {'DESC' if sort == 'bestRatings' else 'ASC'}
            """
        elif sort == "mostRatings" or sort == "leastRatings":
            query = f"""
            SELECT Plane.*, IFNULL(popular.totalratings, 0) AS sort_value, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS avg_rating FROM Plane
            LEFT JOIN popular ON Plane.id = popular.pid
            ORDER BY sort_value {'DESC' if sort == 'mostRatings' else 'ASC'}
        """
        else:
            query = """
                SELECT Plane.*, IFNULL(ratings, 0) * 1.0 / IFNULL(totalratings, 1) AS avg_rating FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                ORDER BY Plane.id DESC
            """
    elif page == "engines":
        if sort == "new" or sort == "old"  or sort == "A-Z" or sort == "Z-A":
            query = f"""
                SELECT Engine.*, IFNULL(ratings, 0) * 1.0 / IFNULL(totalratings, 1) AS avg_rating FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY {'Engine.id' if sort == 'new' or sort == "old" else 'Engine.name'} {"COLLATE NOCASE" if "-" in sort else ""} {'DESC' if sort == 'new' or sort == "Z-A" else 'ASC'} 
            """
        elif sort == "mostViews" or sort == "leastViews":
            query = f"""
                SELECT Engine.*, IFNULL(popular.opened, 0) AS sort_value, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value {'DESC' if sort == 'mostViews' else 'ASC'}
            """
        elif sort == "bestRatings" or sort == "worstRatings":
            query = f"""
                SELECT Engine.*, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS avg_rating FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY avg_rating {'DESC' if sort == 'bestRatings' else 'ASC'}
            """
        elif sort == "mostRatings" or sort == "leastRatings":
            query = f"""
            SELECT Engine.*, IFNULL(popular.totalratings, 0) AS sort_value, IFNULL(popular.ratings, 0) * 1.0 / IFNULL(popular.totalratings, 1) AS avg_rating FROM Engine
            LEFT JOIN popular ON Engine.id = popular.eid
            ORDER BY sort_value {'DESC' if sort == 'mostRatings' else 'ASC'}
        """
        else:
            query = """
                SELECT Engine.*, IFNULL(ratings, 0) * 1.0 / IFNULL(totalratings, 1) AS avg_rating FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY Engine.id DESC
            """
    return query


@app.route("/", methods=["GET"]) # Page route and form methods
def home(): # Page function
    sort_option = request.args.get("Sort", "new") # Fetching the desired sort method to fetch the planes and engines in the corresponding order
    connection, cursor = databaseOpen() # Connecting to the database
    query = databaseSelect('home', sort_option)
    cursor.execute(query) # Executing the query
    pages = cursor.fetchall() # Fetching all the rows
    connection.close() # Closing the connection
    list_of_pages = []
    index = -1
    for i in pages:
        index += 1
        nested_list = []
        for n in i:
            nested_list.append(n)
        list_of_pages.append(nested_list)
        list_of_pages[index][3] = f"data:image/png;base64,{list_of_pages[index][3]}"
    return render_template("home.html", pages=list_of_pages, sort_option=sort_option) # Rendering the home.html file and passing the required variables for Jinja template


@app.route("/planes")
def planes():
    sort_option = request.args.get("Sort", "new")
    connection, cursor = databaseOpen()
    query = databaseSelect('planes', sort_option)
    cursor.execute(query)
    planes = cursor.fetchall()
    connection.close()
    planelist = [[plane[0], plane[1], plane[2], plane[3], plane[-1]] for plane in planes] # Creating nested lists inside the one list with the plane ID, name, description, picture, and avg rating
    index = -1
    for i in planelist:
        index += 1
        planelist[index][3] = f"data:image/png;base64,{planelist[index][3]}"
    return render_template("planes.html", planes=planelist, sort_option=sort_option)


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
        cursor.execute("SELECT ratings, totalratings FROM popular WHERE pid = ?", (plane_id,))
        rating_info = cursor.fetchone()
        if rating_info:
            ratings, totalratings = rating_info
            if totalratings > 0:
                avg_rating = ratings / totalratings
            else:
                avg_rating = 0
        else:
            avg_rating = 0
        connection.close()
        planeimg = f"data:image/png;base64,{plane[3]}"
        return render_template('plane.html', planeid=plane[0], planename=plane[1], planedesc=plane[2], planeimg=planeimg, avgrating=avg_rating)
    else: # If the plane does not exist return a 404 error
        return "Plane not found", 404


@app.route("/engines", methods=["GET"])
def engines():
    sort_option = request.args.get("Sort", "new")
    connection, cursor = databaseOpen()
    query = databaseSelect('engines', sort_option)
    cursor.execute(query)
    engines = cursor.fetchall()
    connection.close()
    enginelist = [[engine[0], engine[1], engine[2], engine[3], engine[-1]] for engine in engines] # Creating nested lists inside the one list with the engine ID, name, description, picture, and avg rating
    index = -1
    for i in enginelist:
        index += 1
        enginelist[index][3] = f"data:image/png;base64,{enginelist[index][3]}"
    return render_template("engines.html", engines=enginelist, sort_option=sort_option)


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
    cursor.execute("SELECT ratings, totalratings FROM popular WHERE eid = ?", (engine_id,))
    rating_info = cursor.fetchone()
    if rating_info:
        ratings, totalratings = rating_info
        if totalratings > 0:
            avg_rating = ratings / totalratings
        else:
            avg_rating = 0
    else:
        avg_rating = 0
    connection.close()
    engineimg = f"data:image/png;base64,{engine[3]}"
    if engine:
        return render_template('engine.html', engineid=engine[0], enginename=engine[1], enginedesc=engine[2], engineimg=engineimg, avgrating=avg_rating)
    else:
        return "Engine not found", 404


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        # Get form data
        plane_engine = request.form.get("PlaneEngine")
        name = request.form.get("name")
        description = request.form.get("description")
        picture = request.form.get("picture")
        password = request.form.get("password")
        # Insert into the database
        connection, cursor = databaseOpen()  # Connecting to the database
        if plane_engine == "plane":
            cursor.execute("INSERT INTO plane (name, description, picture, password) VALUES (?, ?, ?, ?)",
                           (name, description, picture, password))
            connection.commit()
            cursor.execute("SELECT id FROM plane WHERE name = ? AND description = ? AND picture = ? AND password = ?",
                           (name, description, picture, password))
            id = cursor.fetchone()
            cursor.execute("INSERT INTO popular (pid, opened, ratings, totalratings) VALUES (?, 0, 0, 0)",
                           (id[0],))
            connection.commit()
        elif plane_engine == "engine":
            cursor.execute("INSERT INTO engine (name, description, picture, password) VALUES (?, ?, ?, ?)",
                           (name, description, picture, password))
            connection.commit()
            cursor.execute("SELECT id FROM engine WHERE name = ? AND description = ? AND picture = ? AND password = ?",
                           (name, description, picture, password))
            id = cursor.fetchone()
            cursor.execute("INSERT INTO popular (eid, opened, ratings, totalratings) VALUES (?, 0, 0, 0)",
                           (id[0],))
            connection.commit()
        connection.close()
        return render_template("created.html")
    else:
        return render_template("create.html")


@app.route("/edit/<string:item_type>/<int:item_id>", methods=["GET", "POST"])
def edit(item_type, item_id):
    connection, cursor = databaseOpen()

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        picture = request.form["picture"]
        entered_password = request.form["password"]

        # Fetch the current password from the database
        if item_type == "plane":
            cursor.execute("SELECT password FROM Plane WHERE id = ?", (item_id,))
        elif item_type == "engine":
            cursor.execute("SELECT password FROM Engine WHERE id = ?", (item_id,))
        
        current_password = cursor.fetchone()

        if current_password[0] == entered_password:
            if item_type == "plane":
                cursor.execute("""
                    UPDATE Plane
                    SET name = ?, description = ?, picture = ?, password = ?
                    WHERE id = ?
                """, (name, description, picture, entered_password, item_id))
            elif item_type == "engine":
                cursor.execute("""
                    UPDATE Engine
                    SET name = ?, description = ?, picture = ?, password = ?
                    WHERE id = ?
                """, (name, description, picture, entered_password, item_id))

            connection.commit()
            connection.close()
            return redirect(f"/{item_type}/{item_id}")
        else:
            error = "Incorrect password. Please try again."
            item = (name, description)
            connection.close()
            return render_template("edit.html", item_type=item_type, item_id=item_id, item=item, error=error)
    
    if item_type == "plane":
        cursor.execute("SELECT name, description, picture FROM Plane WHERE id = ?", (item_id,))
    elif item_type == "engine":
        cursor.execute("SELECT name, description, picture FROM Engine WHERE id = ?", (item_id,))

    item = cursor.fetchone()
    connection.close()

    if not item:
        return "Item not found", 404

    return render_template("edit.html", item_type=item_type, item_id=item_id, item=item)


@app.route("/search")
def search():
    query = request.args.get("query", "")
    if query:
        connection, cursor = databaseOpen()
        search_query = """
            SELECT id, name, 'plane' AS type FROM Plane WHERE name LIKE ? OR description LIKE ?
            UNION ALL
            SELECT id, name, 'engine' AS type FROM Engine WHERE name LIKE ? OR description LIKE ?
            ORDER BY name COLLATE NOCASE
        """
        search_term = f"%{query}%"
        cursor.execute(search_query, (search_term, search_term, search_term, search_term))
        results = cursor.fetchall()
        connection.close()
        return jsonify({"results": results})
    return jsonify({"results": []})


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