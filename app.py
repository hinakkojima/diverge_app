from flask import Flask, request, redirect, url_for, render_template, session
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

DATA_FILE = "users_data.json"

# ---------------- Helper Functions ----------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def score_match(user1, user2):
    profile1 = user1.get("profile")
    profile2 = user2.get("profile")
    if not profile1 or not profile2:
        return 0
    score = 0

    # Gender match
    if profile2["gender"] == profile1["gender"] or profile2["gender"] in profile1["preferences"]["gender"]:
        score += 2

    # Age difference
    age_diff = abs(profile1["age"] - profile2["age"])
    if age_diff <= 3:
        score += 2
    elif age_diff <= 5:
        score += 1

    # Personality match
    if profile1["personality"] == profile2["personality"]:
        score += 3

    # Interests overlap
    shared_interests = set(profile1["interests"]).intersection(set(profile2["interests"]))
    score += len(shared_interests)

    return score

# ---------------- Routes ----------------

@app.route("/")
def home():
    return "Welcome to the Diverge app!"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        name = request.form["name"]

        data = load_data()
        if any(u["email"] == email for u in data["users"]):
            return "Account already exists. <a href='/login'>Log in here</a>"

        new_user = {"email": email, "password": password, "name": name, "profile": {}}
        data["users"].append(new_user)
        save_data(data)
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        data = load_data()
        user = next((u for u in data["users"] if u["email"] == email and u["password"] == password), None)
        if user:
            session["user_email"] = user["email"]
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials. <a href='/login'>Try again</a>"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        return redirect(url_for("login"))
    return f"Welcome, {session['user_email']}! This is your dashboard."

# ---------------- Deployment Entry ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

