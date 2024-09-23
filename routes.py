from flask import Flask, render_template, request, redirect, jsonify, make_response, render_template_string


import sqlite3
import bcrypt
import base64


app = Flask(__name__)


def databaseOpen():
    connection = sqlite3.connect('planeWIKIDB.db')
    cursor = connection.cursor()
    return connection, cursor


# This function is finding the desired query based off which page the user is
# on and the given search option
def databaseSelect(page, sort):
    query = str()
    if page == "home":
        if sort == "new" or sort == "old":
            query = f"""
                SELECT id, name, description, picture, 'plane' AS type,
                id AS sort_value,
                IFNULL(ratings, 0) * 1.0 /
                IFNULL(totalratings, 1) AS avg_rating FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                UNION ALL
                SELECT id, name, description, picture, 'engine' AS type,
                id AS sort_value,
                IFNULL(ratings, 0) * 1.0 /
                IFNULL(totalratings, 1) AS avg_rating FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value {'DESC' if sort == 'new' else 'ASC'}
            """
        elif sort == "mostViews" or sort == "leastViews":
            query = f"""
                SELECT Plane.id, Plane.name, Plane.description, Plane.picture,
                'plane' AS type,
                IFNULL(popular.opened, 0) AS sort_value,
                IFNULL(popular.ratings, 0) * 1.0 /
                IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                UNION ALL
                SELECT Engine.id, Engine.name, Engine.description,
                Engine.picture, 'engine' AS type,
                IFNULL(popular.opened, 0) AS sort_value,
                IFNULL(popular.ratings, 0) * 1.0 /
                IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value {'DESC' if sort == 'mostViews' else 'ASC'}
            """
        elif sort == "A-Z" or sort == "Z-A":
            query = f"""
                SELECT id, name, description, picture, 'plane' AS type,
                name AS sort_value,
                IFNULL(ratings, 0) * 1.0 /
                IFNULL(totalratings, 1) AS avg_rating
                FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                UNION ALL
                SELECT id, name, description, picture, 'engine' AS type,
                name AS sort_value,
                IFNULL(ratings, 0) * 1.0 /
                IFNULL(totalratings, 1) AS avg_rating
                FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value COLLATE NOCASE {'DESC' if sort == 'Z-A' else 'ASC'}
            """
        elif sort == "bestRatings" or sort == "worstRatings":
            query = f"""
                SELECT Plane.id, Plane.name, Plane.description, Plane.picture,
                'plane' AS type,
                IFNULL(popular.ratings, 0) * 1.0 /
                IFNULL(popular.totalratings, 1) AS sort_value,
                IFNULL(popular.ratings, 0) * 1.0 /
                IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                UNION ALL
                SELECT Engine.id, Engine.name, Engine.description,
                Engine.picture, 'engine' AS type,
                IFNULL(popular.ratings, 0) * 1.0 /
                IFNULL(popular.totalratings, 1) AS sort_value,
                IFNULL(popular.ratings, 0) * 1.0 /
                IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value {'DESC' if sort == 'bestRatings' else 'ASC'}
            """
        elif sort == "mostRatings" or sort == "leastRatings":
            query = f"""
                SELECT Plane.id, Plane.name, Plane.description, Plane.picture,
                'plane' AS type,
                IFNULL(popular.totalratings, 0) AS sort_value,
                IFNULL(popular.ratings, 0) * 1.0 /
                IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                UNION ALL
                SELECT Engine.id, Engine.name, Engine.description,
                Engine.picture, 'engine' AS type,
                IFNULL(popular.totalratings, 0) AS sort_value,
                IFNULL(popular.ratings, 0) * 1.0 /
                IFNULL(popular.totalratings, 1) AS avg_rating
                FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value {'DESC' if sort == 'mostRatings' else 'ASC'}
            """
        else:
            query = """
                SELECT id, name, description, picture, 'plane' AS type,
                id AS sort_value,
                IFNULL(ratings, 0) * 1.0 /
                IFNULL(totalratings, 1) AS avg_rating FROM Plane
                LEFT JOIN popular ON Plane.id = popular.pid
                UNION ALL
                SELECT id, name, description, picture, 'engine' AS type,
                id AS sort_value,
                IFNULL(ratings, 0) * 1.0 /
                IFNULL(totalratings, 1) AS avg_rating FROM Engine
                LEFT JOIN popular ON Engine.id = popular.eid
                ORDER BY sort_value DESC
            """

    elif page == "planes" or page == "engines":
        if sort == "new" or sort == "old" or sort == "A-Z" or sort == "Z-A":
            query = f"""
                SELECT {'Plane' if page == "planes" else "Engine"}.*,
                IFNULL(ratings, 0) * 1.0 / IFNULL(totalratings, 1) AS avg_rating FROM
                {'Plane' if page == "planes" else "Engine"}
                LEFT JOIN popular ON
                {'Plane' if page == "planes" else "Engine"}.id =
                popular.{'pid' if page == "planes" else "eid"}
                ORDER BY {f"{'Plane' if page == 'planes' else 'Engine'}.id" if sort == 'new'
                or sort == "old" else f"{'Plane' if page == 'planes' else 'Engine'}.name"}
                {"COLLATE NOCASE" if "-" in sort else ""}
                {'DESC' if sort == 'new' or sort == "Z-A" else 'ASC'}
            """
        elif sort == "mostViews" or sort == "leastViews":
            query = f"""
                SELECT {'Plane' if page == "planes" else "Engine"}.*,
                IFNULL(popular.opened, 0) AS sort_value,
                IFNULL(popular.ratings, 0) * 1.0 /
                IFNULL(popular.totalratings, 1) AS avg_rating
                FROM {'Plane' if page == "planes" else "Engine"}
                LEFT JOIN popular ON
                {'Plane' if page == "planes" else "Engine"}.id =
                popular.{'pid' if page == "planes" else "eid"}
                ORDER BY sort_value {'DESC' if sort == 'mostViews' else 'ASC'}
            """
        elif sort == "bestRatings" or sort == "worstRatings":
            query = f"""
                SELECT {'Plane' if page == "planes" else "Engine"}.*,
                IFNULL(popular.ratings, 0) * 1.0 /
                IFNULL(popular.totalratings, 1)
                AS avg_rating FROM {'Plane' if page == "planes" else "Engine"}
                LEFT JOIN popular ON
                {'Plane' if page == "planes" else "Engine"}.id =
                popular.{'pid' if page == "planes" else "eid"}
                ORDER BY avg_rating {'DESC' if sort == 'bestRatings' else 'ASC'}
            """
        elif sort == "mostRatings" or sort == "leastRatings":
            query = f"""
                SELECT {'Plane' if page == "planes" else "Engine"}.*,
                IFNULL(popular.totalratings, 0) AS sort_value,
                IFNULL(popular.ratings, 0) * 1.0 /
                IFNULL(popular.totalratings, 1) AS avg_rating FROM
                {'Plane' if page == "planes" else "Engine"}
                LEFT JOIN popular ON
                {'Plane' if page == "planes" else "Engine"}.id =
                popular.{'pid' if page == "planes" else "eid"}
                ORDER BY sort_value {'DESC' if sort == 'mostRatings' else 'ASC'}
            """
        else:
            query = f"""
                SELECT {'Plane' if page == "planes" else "Engine"}.*,
                IFNULL(ratings, 0) * 1.0 /
                IFNULL(totalratings, 1) AS avg_rating FROM
                {'Plane' if page == "planes" else "Engine"}
                LEFT JOIN popular ON
                {'Plane' if page == "planes" else "Engine"}.id =
                popular.{'pid' if page == "planes" else "eid"}
                ORDER BY {'Plane' if page == "planes" else "Engine"}.id DESC
            """
    return query


@app.route("/", methods=["GET"])
def home():
    # Fetching the desired sort method to fetch the planes and engines in the
    # corresponding order
    sort_option = request.args.get("Sort", "new")
    connection, cursor = databaseOpen()
    query = databaseSelect('home', sort_option)
    cursor.execute(query)
    pages = cursor.fetchall()
    connection.close()
    list_of_pages = []
    index = -1
    # Limiting the amount of pages to 10
    for page in pages:
        index += 1
        if index < 10:
            list_of_pages.append([page[0], page[1], page[2], page[3], page[4],
                                  page[-1]])
        else:
            break
    # Turning the images into something that can be processes by html
    index = -1
    for i in list_of_pages:
        index += 1
        list_of_pages[index][3] = f"""data:image/png;base64,
                                  {list_of_pages[index][3]}"""
    return render_template("home.html", pages=list_of_pages,
                           sort_option=sort_option)


@app.route("/planes")
def planes():
    sort_option = request.args.get("Sort", "new")
    connection, cursor = databaseOpen()
    query = databaseSelect('planes', sort_option)
    cursor.execute(query)
    planes = cursor.fetchall()
    connection.close()
    # Creating nested lists inside the one list with the plane ID, name,
    # description, picture, and avg rating
    planelist = []
    index = -1
    for plane in planes:
        index += 1
        if index < 10:
            planelist.append([plane[0], plane[1], plane[2], plane[3],
                              plane[-1]])
        else:
            break
    # Turning the images into something that can be processes by html
    index = -1
    for i in planelist:
        index += 1
        planelist[index][3] = f"data:image/png;base64,{planelist[index][3]}"
    return render_template("planes.html", planes=planelist,
                           sort_option=sort_option)


@app.route("/plane/<string:plane_id>", methods=["GET", "POST"])
def plane(plane_id):
    connection, cursor = databaseOpen()
    if request.method == "POST":
        # Checking if the user has rated the page in the last 24 hours
        review_cookie = request.cookies.get(f"reviewed_plane_{plane_id}")
        if review_cookie:
            return render_template_string("""
            <script>
                alert("You have already submitted a review for this page"
                + " in the last 24 hours.");
                window.history.back();  // Go back to the previous page
            </script>
            """)
        else:
            rating = request.form.get("rating")
            if rating:
                rating = int(rating)
                # Adding the value of the rating and the amount of ratings to
                # the plane in the popular table
                cursor.execute("""
                    UPDATE popular
                    SET ratings = ratings + ?, totalratings = totalratings + 1
                    WHERE pid = ?
                """, (rating, plane_id))
                connection.commit()
                # Inform the user rating was successful and making a cookie
                response = make_response(render_template_string("""
                    <script>
                        alert("Review submitted successfully!");
                        window.history.back();  // Go back to the previous page
                    </script>
                """))
                response.set_cookie(f"reviewed_plane_{plane_id}", "true",
                                    max_age=60*60*24)
                return response

    cursor.execute("SELECT * FROM Plane WHERE id = ?", (plane_id,))
    plane = cursor.fetchone()
    if plane:
        cursor.execute("SELECT opened FROM popular WHERE pid = ?", (plane_id,))
        opened = cursor.fetchone()
        # Checking if the plane exists in the popular table and increasing the
        # amount of times the page has been opened otherwise adding it to the
        # popular table
        if opened:
            opened = opened[0] + 1
            cursor.execute("UPDATE popular SET opened = ? WHERE pid = ?;",
                           (opened, plane_id))
        else:
            cursor.execute("""
                INSERT INTO popular (pid, opened)
                VALUES (?, 1)
            """, (plane_id,))
        connection.commit()
        cursor.execute("""SELECT ratings, totalratings
                       FROM popular WHERE pid = ?""", (plane_id,))
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
        return render_template('plane.html', planeid=plane[0],
                               planename=plane[1], planedesc=plane[2],
                               planeimg=planeimg, avgrating=avg_rating)
    # If the plane does not exist return a 404 error
    else:
        return render_template("404.html"), 404


@app.route("/engines", methods=["GET"])
def engines():
    sort_option = request.args.get("Sort", "new")
    connection, cursor = databaseOpen()
    query = databaseSelect('engines', sort_option)
    cursor.execute(query)
    engines = cursor.fetchall()
    connection.close()
    # Creating nested lists inside the one list with the engine ID, name,
    # description, picture, and avg rating
    enginelist = []
    index = -1
    for engine in engines:
        index += 1
        if index < 10:
            enginelist.append([engine[0], engine[1], engine[2],
                               engine[3], engine[-1]])
        else:
            break
    # Turning the images into something that can be processes by html
    index = -1
    for i in enginelist:
        index += 1
        enginelist[index][3] = f"data:image/png;base64,{enginelist[index][3]}"
    return render_template("engines.html", engines=enginelist,
                           sort_option=sort_option)


@app.route("/engine/<string:engine_id>", methods=["GET", "POST"])
def engine(engine_id):
    connection, cursor = databaseOpen()
    if request.method == "POST":
        # Checking if the user has rated the page in the last 24 hours
        review_cookie = request.cookies.get(f"reviewed_engine_{engine_id}")
        if review_cookie:
            return render_template_string("""
            <script>
                alert("You have already submitted a review for this page"
                + " in the last 24 hours.");
                window.history.back();  // Go back to the previous page
            </script>
            """)
        else:
            rating = request.form.get("rating")
            if rating:
                rating = int(rating)
                cursor.execute("""
                    UPDATE popular
                    SET ratings = ratings + ?, totalratings = totalratings + 1
                    WHERE eid = ?
                """, (rating, engine_id))
                connection.commit()
                # Inform the user rating was successful and making a cookie
                response = make_response(render_template_string("""
                    <script>
                        alert("Review submitted successfully!");
                        window.history.back();  // Go back to the previous page
                    </script>
                """))
                response.set_cookie(f"reviewed_engine_{engine_id}", "true",
                                    max_age=60*60*24)
                return response
    cursor.execute("SELECT * FROM Engine WHERE id = ?", (engine_id,))
    engine = cursor.fetchone()
    cursor.execute("SELECT opened FROM popular WHERE eid = ?", (engine_id,))
    opened = cursor.fetchone()
    if opened:
        opened = opened[0] + 1
        cursor.execute("UPDATE popular SET opened = ? WHERE eid = ?;",
                       (opened, engine_id))
        connection.commit()
    cursor.execute("SELECT ratings, totalratings FROM popular WHERE eid = ?",
                   (engine_id,))
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
        return render_template('engine.html', engineid=engine[0],
                               enginename=engine[1], enginedesc=engine[2],
                               engineimg=engineimg, avgrating=avg_rating)
    else:
        return "Engine not found", 404


@app.route("/create", methods=["GET", "POST"])
def create():
    create_cookie = request.cookies.get("created_page")
    if request.method == "POST":
        # Check if the user has recently created a page
        if create_cookie:
            return render_template_string("""
                <script>
                    alert("You have already created a page recently. " +
                    "Please wait at least an hour before creating another one.");
                    window.history.back();
                </script>
            """)

        plane_engine = request.form.get("PlaneEngine")
        name = request.form.get("name")
        description = request.form.get("description")
        password = request.form.get("password")
        picture_file = request.files.get("picture")

        if picture_file and picture_file.filename != '':
            # Read the file content and convert to base64
            file_data = picture_file.read()
            picture_blob = base64.b64encode(file_data).decode('utf-8')
        # Handle case where no file or invalid file type was uploaded
        else:
            picture_blob = None

        if name and description and password and picture_blob:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'),
                                            bcrypt.gensalt())

            # Insert new data into the plane/engine table, then the popular
            # table
            connection, cursor = databaseOpen()
            if plane_engine == "plane":
                cursor.execute("""INSERT INTO plane (name, description,
                                  picture, password) VALUES (?, ?, ?, ?)""",
                               (name, description, picture_blob,
                                hashed_password))
                connection.commit()
                cursor.execute("""SELECT id FROM plane WHERE name = ?
                                  AND description = ? AND picture = ?
                                  AND password = ?""",
                               (name, description, picture_blob,
                                hashed_password))
                id = cursor.fetchone()
                cursor.execute("""INSERT INTO popular (pid, opened, ratings,
                                  totalratings) VALUES (?, 0, 0, 0)""",
                               (id[0],))
                connection.commit()
            elif plane_engine == "engine":
                cursor.execute("""INSERT INTO engine (name, description,
                                  picture, password) VALUES (?, ?, ?, ?)""",
                               (name, description, picture_blob,
                                hashed_password))
                connection.commit()
                cursor.execute("""SELECT id FROM engine WHERE name = ?
                                  AND description = ? AND picture = ?
                                  AND password = ?""",
                               (name, description, picture_blob,
                                hashed_password))
                id = cursor.fetchone()
                cursor.execute("""INSERT INTO popular (eid, opened, ratings,
                                  totalratings) VALUES (?, 0, 0, 0)""",
                               (id[0],))
                connection.commit()
            connection.close()

            # Set a cookie to restrict further creation and inform of creation
            response = make_response(render_template_string("""
                <script>
                    alert("Page created successfully!");
                    window.location.href = "/";
                </script>
            """))
            response.set_cookie("created_page", "true", max_age=60*60)
            return response

        return render_template("create.html")
    return render_template("create.html")


@app.route("/edit/<string:item_type>/<int:item_id>", methods=["GET", "POST"])
def edit(item_type, item_id):
    connection, cursor = databaseOpen()

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        password = request.form["password"]
        picture_file = request.files.get("picture")

        if picture_file and (picture_file.filename.endswith('.png')
                             or picture_file.filename.endswith('.jpg')
                             or picture_file.filename.endswith('.jpeg')):
            file_data = picture_file.read()
            picture_blob = base64.b64encode(file_data).decode('utf-8')
        else:
            # If no new file is uploaded, keep the existing picture
            if item_type == "plane":
                cursor.execute("SELECT picture FROM Plane WHERE id = ?",
                               (item_id,))
            elif item_type == "engine":
                cursor.execute("SELECT picture FROM Engine WHERE id = ?",
                               (item_id,))
            picture_blob = cursor.fetchone()[0]

        # Fetch the current password hash from the database
        if item_type == "plane":
            cursor.execute("SELECT password FROM Plane WHERE id = ?",
                           (item_id,))
        elif item_type == "engine":
            cursor.execute("SELECT password FROM Engine WHERE id = ?",
                           (item_id,))

        current_password_hash = cursor.fetchone()[0]

        # Check if the password is correct before updating the data
        if bcrypt.checkpw(password.encode('utf-8'), current_password_hash):
            hashed_password = bcrypt.hashpw(password.encode('utf-8'),
                                            bcrypt.gensalt())

            if item_type == "plane":
                cursor.execute("""
                    UPDATE Plane
                    SET name = ?, description = ?, picture = ?, password = ?
                    WHERE id = ?
                """, (name, description, picture_blob, hashed_password,
                      item_id))
            elif item_type == "engine":
                cursor.execute("""
                    UPDATE Engine
                    SET name = ?, description = ?, picture = ?, password = ?
                    WHERE id = ?
                """, (name, description, picture_blob, hashed_password,
                      item_id))

            connection.commit()
            connection.close()
            return redirect(f"/{item_type}/{item_id}")

        else:
            error = "Incorrect password. Please try again."
            item = (name, description, picture_blob)
            connection.close()
            return render_template("edit.html", item_type=item_type,
                                   item_id=item_id, item=item, error=error)

    # Fetching name, description, and picture from the database to show the
    # user what is already there
    if item_type == "plane":
        cursor.execute("""SELECT name, description,
                          picture FROM Plane WHERE id = ?""",
                       (item_id,))
    elif item_type == "engine":
        cursor.execute("""SELECT name, description,
                          picture FROM Engine WHERE id = ?""",
                       (item_id,))

    item = cursor.fetchone()
    connection.close()

    if not item:
        return "Item not found", 404

    return render_template("edit.html", item_type=item_type, item_id=item_id,
                           item=item)


@app.route("/search")
def search():
    query = request.args.get("query", "")
    if query:
        connection, cursor = databaseOpen()
        # Using the user's input to search the plane's and engine's names and
        # description for similarities
        search_query = """
            SELECT id, name, 'plane' AS type FROM Plane WHERE name LIKE ?
            OR description LIKE ?
            UNION ALL
            SELECT id, name, 'engine' AS type FROM Engine WHERE name LIKE ?
            OR description LIKE ?
            ORDER BY name COLLATE NOCASE
        """
        search_term = f"%{query}%"
        cursor.execute(search_query,
                       (search_term, search_term, search_term, search_term))
        results = cursor.fetchall()
        connection.close()
        # Turning the results into something json can understand
        return jsonify({"results": results})
    return jsonify({"results": []})


@app.errorhandler(404)
def not_found(eror):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
