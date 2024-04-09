from flask import Flask, render_template

# import sqlite3


app = Flask(__name__)


@app.route("/")  # ROUTE DECORATOR
def home():     # ROUTE FUNCTION
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)  # live updates code when building a website
