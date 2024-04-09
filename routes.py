from flask import Flask, render_template

# import sqlite3


app = Flask(__name__)


@app.route("/")  # ROUTE DECORATOR
def home():     # ROUTE FUNCTION
    return render_template("home.html")

@app.route("/planes")  # ROUTE DECORATOR
def planes():     # ROUTE FUNCTION
    return render_template("planes.html")

@app.route("/engines")  # ROUTE DECORATOR
def engines():     # ROUTE FUNCTION
    return render_template("engines.html")

@app.route("/create")  # ROUTE DECORATOR
def create():     # ROUTE FUNCTION
    return render_template("create.html")


if __name__ == "__main__":
    app.run(debug=True)  # live updates code when building a website
