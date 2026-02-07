from flask import Flask, render_template, request, redirect, session
import csv
import os
from textblob import TextBlob

app = Flask(__name__)
app.secret_key = "supersecretkey"

ADMIN_FILE = "admin.csv"
REVIEW_FILE = "reviews.csv"


# ---------- HELPER ----------
def admin_exists():
    if not os.path.exists(ADMIN_FILE):
        return False
    with open(ADMIN_FILE, "r", encoding="utf-8") as f:
        return sum(1 for _ in f) > 1  # header + data


# ---------- USER ----------
@app.route("/", methods=["GET", "POST"])
def user_page():
    if request.method == "POST":
        review = request.form["review"]

        sentiment = "Positive" if TextBlob(review).sentiment.polarity >= 0 else "Negative"
        word_count = len(review.split())

        file_exists = os.path.exists(REVIEW_FILE)

        with open(REVIEW_FILE, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["review", "sentiment", "word_count"])
            writer.writerow([review, sentiment, word_count])

        return "Review submitted successfully!"

    return render_template("user.html")


# ---------- ADMIN SIGNUP ----------
@app.route("/admin/signup", methods=["GET", "POST"])
def admin_signup():
    if admin_exists():
        return redirect("/admin/login")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open(ADMIN_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password"])
            writer.writerow([username, password])

        session["admin"] = True
        return redirect("/admin/dashboard")

    return render_template("admin_signup.html")


# ---------- ADMIN LOGIN ----------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if not admin_exists():
        return redirect("/admin/signup")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open(ADMIN_FILE, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == username and row["password"] == password:
                    session["admin"] = True
                    return redirect("/admin/dashboard")

        return "Invalid credentials"

    return render_template("admin_login.html")


# ---------- ADMIN DASHBOARD ----------
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin/login")

    reviews = []
    if os.path.exists(REVIEW_FILE):
        with open(REVIEW_FILE, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            reviews = list(reader)

    return render_template("admin_dashboard.html", reviews=reviews)


# ---------- CLEAR REVIEWS ----------
@app.route("/admin/clear", methods=["GET", "POST"])
def clear_reviews():
    if not session.get("admin"):
        return redirect("/admin/login")

    if os.path.exists(REVIEW_FILE):
        os.remove(REVIEW_FILE)

    return redirect("/admin/dashboard")


# ---------- LOGOUT ----------
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin/login")


if __name__ == "__main__":
    app.run(debug=True)

