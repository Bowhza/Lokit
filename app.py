from flask import Flask, render_template, request, session, redirect, flash
from flask_session import Session
import sqlite3
import os, time
from encryption import hashpass_login, decrypt, load_key, encrypt, hashpass, generate_key

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def connect_db():
    conn = None
    try:
        conn = sqlite3.connect(os.path.realpath('passwords.db'))
    except sqlite3.Error as e:
        print(e)
    return conn

@app.route("/")
def index():
    if not session.get("name"):
        return render_template("index.html")
    return redirect("/fetchdata")

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        conn = connect_db()
        cursor = conn.cursor()
        username = request.form.get("username")
        password = request.form.get("password")
        action = request.form.get("act")

        if action == "Login":
            cursor.execute("""
                SELECT username FROM users
                WHERE username = ?
            """, [username])

            user_result = cursor.fetchone()

            if(user_result == None):
                return render_template("index.html", exists=False)

            cursor.execute("""
            SELECT password FROM users
            WHERE username = ?
            """, [username])
            
            pass_result = cursor.fetchone()
            
            cursor.execute("""
                SELECT salt FROM users
                WHERE username = ?
            """, [username])

            salt = cursor.fetchone()
            conn.close()

            if pass_result[0] != hashpass_login(password, salt[0]):
                return render_template("index.html", failed=True)

            session["name"] = username
            return redirect("/")
        
@app.route("/fetchdata")
def fetchdata():
    conn = connect_db()
    cursor = conn.cursor()
    username = session["name"]
    try:
        key = load_key(username)
    except:
        return "Key could not be loaded. Make sure its in the root directory."

    nav_btns = {"new-pass":"New Password", 
                "change-master-pass":"Change Master Password", 
                "delete-master":"Delete Master Account"}

    #Fetches the usernames
    cursor.execute(f"""
    SELECT username FROM accounts
    WHERE user_id = '{username}'
    """)
    usernames = cursor.fetchall()

    #Fetched the passwords
    cursor.execute(f"""
    SELECT password FROM accounts
    WHERE user_id = '{username}'
    """)
    passwords = cursor.fetchall()

    decrypted = []

    #Decrypts the passwords
    for password in passwords:
        for item in password:
            decrypted.append(decrypt(item, key))

    #Fetches the application name
    cursor.execute(f"""
    SELECT application FROM accounts
    WHERE user_id = '{username}'
    """)
    app = cursor.fetchall()

    #Fetches the URL or the website
    cursor.execute(f"""
    SELECT web_link FROM accounts
    WHERE user_id = '{username}'
    """)
    web = cursor.fetchall()

    cursor.execute(f"""
    SELECT row_id FROM accounts
    WHERE user_id = '{username}'
    """)
    rowid = cursor.fetchall()
    conn.close()

    return render_template("account.html", data=zip(usernames, decrypted, app, web, rowid), nav_btns=nav_btns)

@app.route("/addaccount", methods=["GET", "POST"])
def addaccount():
    if request.method == "POST":
        username = session["name"]
        try:
            key = load_key(username)
        except:
            return "Key could not be loaded. Make sure its in the root directory."
        
        conn = connect_db()
        cursor = conn.cursor()

        formusername = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        application = request.form.get("application")
        link = request.form.get("link")

        if username.strip() == "":
            return "Username cannot be empty. Prevented form submission."
        if password1 != password2:
            return "Passwords do not match. Prevented form submission."
        if password1.strip() == "" or password2.strip() == "":
            return "Cannot have empty fields for passwords."
        if application.strip() == "":
            return "Cannot have empty application name."
        if link.strip() == "":
            link = "Not Available."

        encrypted_password = encrypt(password1, key)

        user_info = (formusername, encrypted_password, link, application)
        cursor.execute(f"""
            INSERT INTO accounts (user_id, username, password, web_link, application)
            VALUES((SELECT username FROM users WHERE username = '{username}'),?,?,?,?)
            """, user_info)
        conn.commit()
        conn.close()

        return redirect("/")
    
@app.route("/removepass", methods=["GET", "POST"])
def removepass():
    conn = connect_db()
    conn.row_factory = lambda cursor,row: row[0]
    cursor = conn.cursor()
    username = session["name"]
    rowid_form = request.form.get("id")

    cursor.execute("""
    SELECT row_id FROM accounts
    WHERE user_id = ?
    """, [username])

    rowid = cursor.fetchall()
    print(rowid)
    print(rowid_form)

    if int(rowid_form) in rowid:
        print("TRIGGERED")
        cursor.execute("""
        DELETE FROM accounts
        WHERE row_id = ?
        """, [rowid_form])

    conn.commit()
    conn.close()
    return redirect("/fetchdata")


@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port="8080", debug=True)