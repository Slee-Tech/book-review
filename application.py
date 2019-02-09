import os

from flask import Flask, session, flash, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import lookup

#from helpers import apology

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

API_KEY = os.getenv("KEY")

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

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        if not request.form.get("search_books"):
            return render_template("error.html", error="No book entered")
        books = request.form.get("search_books") + "%"

        results = db.execute("SELECT title FROM books WHERE isbn LIKE :search OR author LIKE :search OR title LIKE :search", {"search":books}).fetchall()
        #results = db.execute("SELECT title FROM books WHERE author LIKE :search", {"search":books}).fetchall()
        db.commit()
        if not results:
            return render_template("error.html", error="No results or query failed")
        return render_template("books.html", books=results)
        
    return render_template("search.html")

@app.route("/search/<string:book_title>",  methods=["GET","POST"] )
def book(book_title):
    book_info = db.execute("SELECT * FROM books WHERE title = :title", {"title":book_title}).fetchone()
    db.commit()
    if book_info is None:
        return render_template("error.html", error = "Sorry no details for this title.") 
    book_reviews = db.execute("SELECT review FROM reviews JOIN books ON reviews.isbn = books.isbn WHERE reviews.isbn = :b_isbn", {"b_isbn":book_info["isbn"]}).fetchall()
    if book_reviews is None:
        book_reviews="No reviews found."

    goodreads_info = lookup(API_KEY, book_info["isbn"])
    #print(goodreads_info)
    return render_template("book.html", info=book_info, reviews=book_reviews, gr=goodreads_info)
    
    


@app.route("/rating/<string:book_isbn>", methods=["POST"])
def rating(book_isbn):
    if not request.form.get("rate"):
        return render_template("error.html", error="No rating submitted.")
    if not request.form.get("review"):
        return render_template("error.html", error="No review submitted.")
    
    rated = request.form.get("rate")
    review = request.form.get("review")
    isbn = book_isbn
    id = session["user_id"]

    submit_review = db.execute("INSERT INTO reviews (isbn, user_id, rating, review) VALUES(:_isbn, :userid, :user_rating, :user_review)", {"_isbn":isbn, "userid":id, "user_rating":rated,"user_review":review})
    db.commit()
    if not submit_review:
        return render_template("error.html", error="There was an error submitting the review.")
    return render_template("error.html", error="Your review was successfully submitted.")









