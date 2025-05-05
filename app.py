import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

# Secret key from environment variable (or fallback)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# File to store user data
DATA_FILE = "users_data.json"

# Load user data
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Save user data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")

        data = load_data()

        # Check if email already exists
        for user in data["users"]:
            if user["email"] == email:
                flash("Account already exists. Log in instead.")
                return redirect(url_for("login"))

        # Save new user
        new_user = {
            "email": email,
            "password": password,
            "name": name,
            "profile": {}
        }
        data["users"].append(new_user)
        save_data(data)

        flash("Account created. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        data = load_data()

        for user in data["users"]:
            if user["email"] == email and user["password"] == password:
                session["user"] = user["email"]
                flash("Welcome back!")
                return redirect(url_for("dashboard"))

        flash("Invalid credentials. Try again.")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    data = load_data()
    user = next((u for u in data["users"] if u["email"] == session["user"]), None)
    return render_template("dashboard.html", user=user)

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You’ve been logged out.")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=(os.environ.get("FLASK_ENV") != "production"))

