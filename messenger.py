from flask import Blueprint, request, session, render_template, redirect, current_app, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from os import path, makedirs

messenger = Blueprint("messenger", __name__, template_folder="templates", static_folder="static")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#        БАЗА ДАННЫХ
def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host="127.0.0.1",
            database="vlad_frank_knowledge_base",
            user="vlad_frank_knowledge_base",
            password="123"
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        db_path = path.join(path.dirname(path.realpath(__file__)), "messenger.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

#        ИНИЦИАЛИЗАЦИЯ SQLite
@messenger.route("/messenger/init_sqlite")
def init_sqlite():
    conn, cur = db_connect()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lovina_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        avatar TEXT DEFAULT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(sender_id) REFERENCES lovina_users(id),
        FOREIGN KEY(receiver_id) REFERENCES lovina_users(id)
    );
    """)
    db_close(conn, cur)
    return "SQLite initialized"


#          ВАЛИДАЦИЯ
import re
LOGIN_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
PASS_RE = re.compile(r"^[A-Za-z0-9!@#$%^&*()._-]{6,64}$")

def validate_login(login):
    return login and LOGIN_RE.match(login)

def validate_password(password):
    return password and PASS_RE.match(password)


#      НЕАВТОРИЗОВАННАЯ СТРАНИЦА
@messenger.route("/messenger/")
def messenger_main():
    if "user_id" not in session:
        return render_template("welcome.html", fio="Владислав Франк", group="ФБИ-31")
    return redirect("/messenger/home")


#          РЕГИСТРАЦИЯ
@messenger.route("/messenger/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", fio="Владислав Франк", group="ФБИ-31")

    login = request.form.get("login")
    password = request.form.get("password")
    full_name = request.form.get("full_name")
    file = request.files.get("avatar")

    if not validate_login(login):
        return render_template("register.html", error="Неверный формат логина")
    if not validate_password(password):
        return render_template("register.html", error="Неверный пароль")

    avatar_path = None
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{login}_{file.filename}")
        avatar_dir = path.join(current_app.root_path, 'static', 'avatars')
        makedirs(avatar_dir, exist_ok=True)
        file.save(path.join(avatar_dir, filename))
        avatar_path = f"/static/avatars/{filename}"

    conn, cur = db_connect()
    if current_app.config["DB_TYPE"] == "postgres":
        cur.execute("SELECT id FROM lovina_users WHERE login=%s", (login,))
    else:
        cur.execute("SELECT id FROM lovina_users WHERE login=?", (login,))
    if cur.fetchone():
        db_close(conn, cur)
        return render_template("register.html", error="Пользователь уже существует")

    password_hash = generate_password_hash(password)
    if current_app.config["DB_TYPE"] == "postgres":
        cur.execute("""
            INSERT INTO lovina_users (login, password_hash, full_name, role, avatar)
            VALUES (%s, %s, %s, 'user', %s)""",
            (login, password_hash, full_name, avatar_path)
        )
    else:
        cur.execute("""
            INSERT INTO lovina_users (login, password_hash, full_name, role, avatar)
            VALUES (?, ?, ?, 'user', ?)""",
            (login, password_hash, full_name, avatar_path)
        )

    db_close(conn, cur)
    return redirect("/messenger/login")


#              ЛОГИН
@messenger.route("/messenger/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", fio="Владислав Франк", group="ФБИ-31")

    login_val = request.form.get("login")
    password = request.form.get("password")

    conn, cur = db_connect()
    if current_app.config["DB_TYPE"] == "postgres":
        cur.execute("SELECT * FROM lovina_users WHERE login=%s", (login_val,))
    else:
        cur.execute("SELECT * FROM lovina_users WHERE login=?", (login_val,))
    user = cur.fetchone()
    db_close(conn, cur)

    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Неверный логин или пароль")

    session["user_id"] = user["id"]
    session["login"] = user["login"]
    session["role"] = user["role"]
    session["avatar"] = user.get("avatar")
    return redirect("/messenger/home")


#          ВЫХОД
@messenger.route("/messenger/logout")
def logout():
    session.clear()
    return redirect("/messenger/")


#     ГЛАВНАЯ СТРАНИЦА ПОСЛЕ ЛОГИНА
@messenger.route("/messenger/home")
def home():
    if "user_id" not in session:
        return redirect("/messenger/")
    return render_template("home.html", fio="Владислав Франк", group="ФБИ-31", avatar=session.get("avatar"))


#      СПИСОК ВСЕХ ПОЛЬЗОВАТЕЛЕЙ
@messenger.route("/messenger/users")
def list_users():
    if "user_id" not in session:
        return redirect("/messenger/")
    conn, cur = db_connect()
    cur.execute("SELECT id, login, full_name, avatar FROM lovina_users")
    users = cur.fetchall()
    db_close(conn, cur)
    return render_template("users.html", fio="Владислав Франк", group="ФБИ-31", users=users)


#       ЧАТ С ОПРЕДЕЛЁННЫМ ЧЕЛОВЕКОМ
@messenger.route("/messenger/chat/<int:uid>")
def chat(uid):
    if "user_id" not in session:
        return redirect("/messenger/")
    conn, cur = db_connect()
    cur.execute("SELECT * FROM lovina_users WHERE id=%s" if current_app.config["DB_TYPE"]=="postgres"
                else "SELECT * FROM lovina_users WHERE id=?", (uid,))
    user = cur.fetchone()

    if current_app.config["DB_TYPE"] == "postgres":
        cur.execute("""
            SELECT m.id, m.sender_id, m.receiver_id, m.content AS text, m.created_at,
                   u.avatar AS sender_avatar
            FROM messages m
            JOIN lovina_users u ON u.id = m.sender_id
            WHERE (m.sender_id=%s AND m.receiver_id=%s) OR (m.sender_id=%s AND m.receiver_id=%s)
            ORDER BY m.created_at
        """, (session["user_id"], uid, uid, session["user_id"]))
    else:
        cur.execute("""
            SELECT m.id, m.sender_id, m.receiver_id, m.content AS text, m.created_at,
                   u.avatar AS sender_avatar
            FROM messages m
            JOIN lovina_users u ON u.id = m.sender_id
            WHERE (m.sender_id=? AND m.receiver_id=?) OR (m.sender_id=? AND m.receiver_id=?)
            ORDER BY m.created_at
        """, (session["user_id"], uid, uid, session["user_id"]))
    messages = cur.fetchall()
    db_close(conn, cur)
    return render_template("chat.html", fio="Владислав Франк", group="ФБИ-31", user=user, messages=messages)


#         ОТПРАВКА СООБЩЕНИЯ
@messenger.route("/messenger/send", methods=["POST"])
def send():
    if "user_id" not in session:
        return jsonify({"error": "not auth"}), 403

    receiver_id = request.form.get("receiver_id")
    text = request.form.get("text")
    if not text or len(text.strip())==0:
        return jsonify({"error": "Пустое сообщение"}), 400

    conn, cur = db_connect()
    ts = datetime.now().isoformat()
    if current_app.config["DB_TYPE"] == "postgres":
        cur.execute("""
            INSERT INTO messages (sender_id, receiver_id, content, created_at)
            VALUES (%s, %s, %s, %s)
        """, (session["user_id"], receiver_id, text, ts))
    else:
        cur.execute("""
            INSERT INTO messages (sender_id, receiver_id, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (session["user_id"], receiver_id, text, ts))
    db_close(conn, cur)
    return jsonify({"ok": True})


#        УДАЛЕНИЕ СООБЩЕНИЯ
@messenger.route("/messenger/delete_message/<int:msg_id>", methods=["POST"])
def delete_message(msg_id):
    if "user_id" not in session:
        return jsonify({"error": "not auth"}), 403

    conn, cur = db_connect()
    if current_app.config["DB_TYPE"]=="postgres":
        cur.execute("DELETE FROM messages WHERE id=%s AND (sender_id=%s OR receiver_id=%s)",
                    (msg_id, session["user_id"], session["user_id"]))
    else:
        cur.execute("DELETE FROM messages WHERE id=? AND (sender_id=? OR receiver_id=?)",
                    (msg_id, session["user_id"], session["user_id"]))
    db_close(conn, cur)
    return jsonify({"ok": True})


#      УДАЛЕНИЕ АККАУНТА
@messenger.route("/messenger/delete_account", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        return redirect("/messenger/")

    uid = session["user_id"]
    conn, cur = db_connect()
    cur.execute("DELETE FROM messages WHERE sender_id=? OR receiver_id=?" if current_app.config["DB_TYPE"]=="sqlite"
                else "DELETE FROM messages WHERE sender_id=%s OR receiver_id=%s", (uid, uid))
    cur.execute("DELETE FROM lovina_users WHERE id=?" if current_app.config["DB_TYPE"]=="sqlite"
                else "DELETE FROM lovina_users WHERE id=%s", (uid,))
    db_close(conn, cur)
    session.clear()
    return redirect("/messenger/")


#              АДМИН
@messenger.route("/messenger/admin")
def admin():
    if session.get("role") != "admin":
        return "Access denied", 403

    conn, cur = db_connect()
    cur.execute("SELECT id, login, full_name, role, avatar FROM lovina_users")
    users = cur.fetchall()
    db_close(conn, cur)
    return render_template("admin.html", users=users)

@messenger.route("/messenger/admin/delete/<int:uid>")
def admin_delete(uid):
    if session.get("role") != "admin":
        return "Forbidden", 403

    conn, cur = db_connect()
    cur.execute("DELETE FROM lovina_users WHERE id=?" if current_app.config["DB_TYPE"]=="sqlite"
                else "DELETE FROM lovina_users WHERE id=%s", (uid,))
    db_close(conn, cur)
    return redirect("/messenger/admin")
