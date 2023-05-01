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

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("name"):
        return redirect("/fetchdata")

    if request.method == "POST":
        conn = connect_db()
        cursor = conn.cursor()

        username = request.form.get("username")
        password = request.form.get("password")
        confirmpass = request.form.get("confirmpass")

        try:
            cursor.execute("""
            SELECT username
            FROM users
            WHERE username = ?
            """,[username])
            query = cursor.fetchone();

            if(query != None):
                return render_template("register.html", exists=True)

        except sqlite3.Error as e:
            return str(e)

        if(password != confirmpass):
            return render_template("register.html", match=False)
        
        else:
            
            hashed, salt = hashpass(password)
            generate_key(username)
            key = load_key(username)

            user_info = [username, hashed, salt, key]

            try:
                cursor.execute("""
                INSERT INTO users VALUES (?,?,?,?)
                """, (user_info[0], user_info[1], user_info[2], user_info[3]))
                conn.commit()

            except sqlite3.Error as e:
                return str(e)

            return render_template("index.html", success=True)

    if request.method == "GET":
        return render_template("register.html")


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

@app.route("/changepass", methods=["GET", "POST"])
def changepass():
    if request.method == "GET":
        return """
        <div class="modal-content">
            <button class="close-btn">&times;</button>
            <h2>Change Master Password</h2>
            <form id="change-pass-form" action="/changepass" onsubmit="return changePassValidation()" method="post">
                <div>
                    <label for="currentpass">Password</label>
                    <input type="password" name="currentpass" required>
                </div>
                <div>
                    <label for="newpassword">New Password</label>
                    <input type="password" name="newpassword" required>
                </div>
                <div>
                    <label for="confirmpassword">Confirm Password</label>
                    <input type="password" name="confirmpassword" required>
                </div>
                <div>
                    <p id="matching-text"></p>
                    <button type="submit" class="submit-btn">Submit</button>
                </div>
            </form>
        </div>
        """
    if request.method == "POST":
        
        conn = connect_db()
        cursor = conn.cursor()

        username = session["name"]
        currentpass = request.form.get("currentpass")
        newpass = request.form.get("newpassword")
        confirmpass = request.form.get("confirmpassword")
        
        cursor.execute("""
        SELECT password FROM users
        WHERE username = ?
        """, [username])
        password = cursor.fetchone()

        cursor.execute("""
        SELECT salt FROM users
        WHERE username = ?
        """, [username])
        salt = cursor.fetchone()
        

        if(hashpass_login(currentpass, salt[0]) != password[0]):
            return "The password you entered does not match your current password."

        elif(hashpass_login(currentpass, salt[0]) == password[0]):
            return "Cannot change password to your current password."

        elif(newpass != confirmpass):
            return "The two passwords do not match."
        
        else:
            try:
                hashed, salt = hashpass(newpass)
                cursor.execute("""
                UPDATE users
                SET password = ?,
                    salt = ?
                WHERE username = ?;
                """, (hashed, salt, username))
                conn.commit()
            except sqlite3.Error as e:
                return str(e)

        return redirect("/fetchdata")
    
@app.route("/deleteacc", methods=["GET", "POST"])
def deleteacc():
    if request.method == "GET":
        return """
        <div class="modal-content">
            <button class="close-btn">&times;</button>
            <h2>Delete Master Account</h2>
            <form id="delete-acc-form" action="/deleteacc" onsubmit="return formValidation()" method="post">
                <div>
                    <label for="password">Password</label>
                    <input type="password" name="password" required>
                </div>
                <div>
                    <label for="confirmpassword">Confirm Password</label>
                    <input type="password" name="confirmpassword" required>
                </div>
                <div>
                    <p id="matching-text"></p>
                    <button type="submit" class="submit-btn">Submit</button>
                </div>
            </form>
        </div>
        """
    if request.method == "POST":
        
        conn = connect_db()
        cursor = conn.cursor()

        username = session["name"]
        password = request.form.get("password")
        confirmpass = request.form.get("confirmpassword")

        cursor.execute("""
        SELECT password FROM users
        WHERE username = ?
        """, [username])
        dbpassword = cursor.fetchone()

        cursor.execute("""
        SELECT salt FROM users
        WHERE username = ?
        """, [username])
        salt = cursor.fetchone()

        if(password != confirmpass): 
            return "Password fields do not match."
        
        elif(hashpass_login(password, salt[0]) != dbpassword[0]):
            return "Password entered does not match the account password."
        
        else:
            try:
                cursor.execute("""
                DELETE FROM accounts
                WHERE user_id = ?
                """, [username])

                cursor.execute("""
                DELETE FROM users
                WHERE username = ?
                """, [username])

                conn.commit()

                os.remove(f"{username}.key")

            except sqlite3.Error as e:
                return str(e)
            
        session["name"] = None
        return redirect("/")
        
@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)