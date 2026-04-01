from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "secret123"

# قاعدة البيانات
def init_db():
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# تسجيل مستخدم جديد
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        try:
            conn = sqlite3.connect("app.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return "اسم المستخدم موجود مسبقًا"
    return render_template("register.html")

# تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("app.db")
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[0], password):
            session["username"] = username
            return redirect("/inbox")
        else:
            return "اسم المستخدم أو كلمة المرور خطأ"
    return render_template("login.html")

# صندوق الرسائل
@app.route("/inbox")
def inbox():
    if "username" not in session:
        return redirect("/login")
    username = session["username"]
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    c.execute("SELECT sender, message FROM messages WHERE receiver=?", (username,))
    messages = c.fetchall()
    conn.close()
    return render_template("inbox.html", messages=messages)

# إرسال رسالة
@app.route("/send", methods=["GET", "POST"])
def send():
    if "username" not in session:
        return redirect("/login")
    if request.method == "POST":
        receiver = request.form["receiver"]
        message = request.form["message"]
        sender = session["username"]

        # التحقق أن المستقبل موجود
        conn = sqlite3.connect("app.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (receiver,))
        user = c.fetchone()
        if not user:
            conn.close()
            return "المستخدم المستقبل غير موجود"
        c.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", (sender, receiver, message))
        conn.commit()
        conn.close()
        return redirect("/inbox")
    return render_template("send.html")

# تسجيل خروج
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
