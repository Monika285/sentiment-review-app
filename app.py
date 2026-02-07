from flask import Flask, render_template, request, redirect, session, url_for
import csv
import os
import uuid
import time
from textblob import TextBlob

app = Flask(__name__)
app.secret_key = "supersecretkey"

ADMIN_FILE = "admin.csv"
REVIEW_FILE = "reviews.csv"
RESET_TOKEN_FILE = "reset_tokens.csv"
TOKEN_EXPIRY_SECONDS = 15 * 60  # 15 minutes


# ---------- HELPERS ----------

def admin_exists():
    if not os.path.exists(ADMIN_FILE):
        return False
    with open(ADMIN_FILE, "r", encoding="utf-8") as f:
        return sum(1 for _ in f) > 1


def save_reset_token(email, token):
    file_exists = os.path.exists(RESET_TOKEN_FILE)
    with open(RESET_TOKEN_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["email", "token", "timestamp"])
        writer.writerow([email, token, int(time.time())])


def get_valid_email_from_token(token):
    if not os.path.exists(RESET_TOKEN_FILE):
        return None

    with open(RESET_TOKEN_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["token"] == token:
                if int(time.time()) - int(row["timestamp"]) <= TOKEN_EXPIRY_SECONDS:
                    return row["email"]
    return None


def update_admin_password(email, new_password):
    rows = []
    with open(ADMIN_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["email"] == email:
                row["password"] = new_password
            rows.append(row)

    with open(ADMIN_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["email", "username", "password"])
        writer.writeheader()
        writer.writerows(rows)


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

        return redirect("/")

    return render_template("user.html")


# ---------- ADMIN SIGNUP ----------

@app.route("/admin/signup", methods=["GET", "POST"])
def admin_signup():
    if admin_exists():
        return redirect("/admin/login")

    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        with open(ADMIN_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["email", "username", "password"])
            writer.writerow([email, username, password])

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


# ---------- FORGOT PASSWORD ----------

@app.route("/admin/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]

        token = str(uuid.uuid4())
        save_reset_token(email, token)

        reset_link = url_for("reset_password", token=token, _external=True)

        # Simulated email (industry interview-friendly)
        print("==== PASSWORD RESET EMAIL ====")
        print("Reset link:", reset_link)
        print("Link valid for 15 minutes")
        print("==============================")

        return "Password reset link sent to email (check server console)."

    return render_template("forgot_password.html")


# ---------- RESET PASSWORD ----------

@app.route("/admin/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = get_valid_email_from_token(token)
    if not email:
        return "Invalid or expired token."

    if request.method == "POST":
        new_password = request.form["password"]
        update_admin_password(email, new_password)
        return redirect("/admin/login")

    return render_template("reset_password.html")


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

@app.route("/admin/clear", methods=["POST"])
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
    