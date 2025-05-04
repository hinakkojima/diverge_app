from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

DATA_FILE = "users_data.json"

# Load users from file
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Save users to file
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Home Page
@app.route("/")
def home():
    return render_template("home.html")

# Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    show_login_button = False

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        name = request.form["name"]

        data = load_data()

        # If user already exists
        if any(user["email"] == email for user in data["users"]):
            flash("Account already exists. Log in instead.")
            show_login_button = True
            return render_template("register.html", 
show_login_button=show_login_button)

        # Otherwise, create user
        new_user = {
            "email": email,
            "password": password,
            "name": name,
            "profile": {}
        }

        data["users"].append(new_user)
        save_data(data)

        flash("Account created successfully!")
        return redirect(url_for("login"))

    return render_template("register.html", show_login_button=show_login_button)

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        data = load_data()
        for user in data["users"]:
            if user["email"] == email and user["password"] == password:
                session["user"] = user["email"]
                flash("Logged in successfully!")
                return redirect(url_for("dashboard"))

        flash("Incorrect email or password.")
        return redirect(url_for("login"))

    return render_template("login.html")

# Dashboard Page
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))
    return f"Welcome, {session['user']}! This is your dashboard."

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.")
    return redirect(url_for("home"))

# Run app
if __name__ == "__main__":
    app.run(debug=True)

