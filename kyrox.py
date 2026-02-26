"""
KyroX Web Application
Clean Production Version
"""
from flask import jsonify, request
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from pathlib import Path
import sqlite3
import json
import os
from flask import Flask


# ==============================
# CONFIG
# ==============================


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32))

# ==============================
# DATABASE INIT
# ==============================

def init_db():
    conn = sqlite3.connect("kyrox.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        plan TEXT DEFAULT 'free'
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ==============================
# USER-SPECIFIC DATA FUNCTIONS
# ==============================

def get_user_file():
    username = session.get("username")
    if not username:
        return None
    return Path("data") / f"{username}.json"


def load_data():
    file_path = get_user_file()

    if not file_path or not file_path.exists():
        return {"revenues": [], "expenses": [], "tasks": []}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"revenues": [], "expenses": [], "tasks": []}


def save_data(data):
    file_path = get_user_file()
    if not file_path:
        return

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_dashboard_summary(plan):
    data = load_data()

    revenue = sum(item.get("amount", 0) for item in data["revenues"])
    expense = sum(item.get("amount", 0) for item in data["expenses"])
    profit = revenue - expense
    profit_margin = (profit / revenue * 100) if revenue > 0 else 0

    # =====================
    # FREE PLAN AI
    # =====================
    if plan == "free":
        if revenue == 0:
            insight = "No revenue recorded yet."
        elif profit < 0:
            insight = "Business is running at a loss."
        else:
            insight = "Business performance looks stable."

    # =====================
    # PRO PLAN AI
    # =====================
    else:
        growth_rate = ((revenue - expense) / revenue * 100) if revenue > 0 else 0

        if revenue == 0:
            insight = "KyroX AI: No revenue detected. Immediate monetization strategy required."

        elif profit < 0:
            insight = "KyroX AI Critical Alert: Negative profitability detected. Recommend reducing fixed costs and increasing pricing efficiency."

        elif expense > revenue * 0.75:
            insight = "KyroX AI Warning: Operational cost ratio exceeds optimal 75%. Recommend expense restructuring."

        elif growth_rate > 40:
            insight = "KyroX AI: Exceptional growth detected. Scaling opportunity with strong financial stability."

        else:
            insight = "KyroX AI Analysis: Stable performance with moderate margin. Strategic reinvestment recommended."

    return {
        "revenue": revenue,
        "expense": expense,
        "profit": profit,
        "profit_margin": round(profit_margin, 2),
        "insight": insight
    }
def generate_ai_response(message, plan):
    message = message.lower()

    # IDEA REQUEST
    if "idea" in message:
        if plan == "pro":
            return """
🔥 Pro AI Ideas:
1) AI automation service for small shops
2) Instagram reel editing agency
3) WhatsApp chatbot setup for local businesses
4) AI content writing service for startups
"""
        else:
            return """
💡 Free Plan Idea:
Start a niche Instagram theme page and monetize with affiliate links.

Upgrade to Pro for advanced business ideas.
"""

    # GROWTH STRATEGY
    elif "grow" in message or "scale" in message:
        return """
📈 Growth Strategy:
- Pick ONE niche
- Build 3 sample projects
- DM 20 potential clients daily
- Improve based on feedback
Consistency = growth.
"""

    # TRACKING
    elif "track" in message or "progress" in message:
        return """
📊 Track These Daily:
- Revenue
- Expenses
- New Customers
- Conversion Rate
- Social Media Reach

What gets measured gets improved.
"""

    # MOTIVATION
    elif "motivate" in message:
        return "🚀 Small progress daily beats big plans never started."

    # DEFAULT
    else:
        return """
🤖 I am KyroX Smart Advisor.

You can ask me about:
- Business ideas
- Growth strategy
- Tracking progress
- Scaling advice
"""
# ==============================
# ROUTES
# ==============================

@app.route("/")
def home():
    if "username" in session:
        return redirect("/dashboard")
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")

    plan = session.get("plan", "free")
    summary = get_dashboard_summary(plan)

    return render_template("dashboard.html", data=summary)    
@app.route("/upgrade")
def upgrade():
    if "username" not in session:
        return redirect("/login")

    return render_template("upgrade.html")
@app.route("/process_payment")
def process_payment():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    conn = sqlite3.connect("kyrox.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET plan = 'pro' WHERE username = ?", (username,))
    conn.commit()
    conn.close()

    session["plan"] = "pro"

    return redirect("/dashboard")
@app.route("/chat", methods=["POST"])
def chat():
    if "username" not in session:
        return jsonify({"reply": "Please login first."})

    user_message = request.json.get("message")
    plan = session.get("plan", "free")

    reply = generate_ai_response(user_message, plan)

    return jsonify({"reply": reply})
# ------------------------------
# LOGIN
# ------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("kyrox.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password, plan FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session["username"] = username
            session["plan"] = user[1]
            return redirect("/")

        return "❌ Invalid username or password"

    return render_template("login.html")


# ------------------------------
# REGISTER
# ------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        hashed = generate_password_hash(password)

        conn = sqlite3.connect("kyrox.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "❌ Username already exists"

        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ------------------------------
# LOGOUT
# ------------------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ------------------------------
# ADD TRANSACTION
# ------------------------------

@app.route("/add", methods=["POST"])
def add_transaction():
    if "username" not in session:
        return redirect("/login")

    data = load_data()

    # Count total transactions
    total_transactions = len(data["revenues"]) + len(data["expenses"])

    # Free plan limit
    if session.get("plan") == "free" and total_transactions >= 20:
        return "Free plan limit reached. Upgrade to Pro."

    transaction = {
        "type": request.form["type"],
        "category": request.form["category"],
        "amount": float(request.form["amount"]),
        "note": request.form["note"]
    }

    if transaction["type"] == "revenue":
        data["revenues"].append(transaction)
    else:
        data["expenses"].append(transaction)

    save_data(data)

    return redirect("/")

# ==============================
# RUN APP
# ==============================

if __name__ == "__main__":
    print("🚀 KyroX Web App Running")
    print("🌍 http://127.0.0.1:5000")

    app.run(debug=True)