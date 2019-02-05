import os

from flask import Flask, session, flash, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

#from helpers import apology

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if session.get("user_id") is None:
        return redirect("/login")
    else:
        return render_template("index.html", name=session["name"])
    
    #if request.method == "POST":
        #return render_template("error.html", error="Success")
    #else:
        #return render_template("error.html", error="You got here via GET")

@app.route("/login",  methods=["GET", "POST"])
def login():
    
    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", error="No username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", error="No password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username":request.form.get("username")}).fetchone()
        db.commit()

        # Ensure username exists and password is correct
        if not rows or not check_password_hash(rows["hash"], request.form.get("password")):
            return render_template("error.html", error="username or password doesn't match")

        # Remember which user has logged in, maybe use this for buy query
        session["user_id"] = rows["id"]
        session["name"] = rows["username"]

        # Redirect user to home page
        return render_template("index.html", name=session["name"])


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

    

@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("login.html")

                # ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html")

                # ensure password and verified password is the same
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("login.html")

        hash = generate_password_hash(request.form.get("password"))
        user = request.form.get("username")

                # insert the new user into users, storing the hash of the user's password
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", {"username":user, "hash":hash})
        db.commit()

        #if not result:
            #return render_template("register.html")

        #session["user_id"] = result.

        # redirect user to home page
        return redirect("/login")

    else:
        return render_template("register.html")





