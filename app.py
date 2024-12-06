#------------------------------------------------------
# LOKIT - Local Network Password Manager
#------------------------------------------------------
# Created by: https://github.com/Bowhza
#------------------------------------------------------

#Imports required libraries.
from flask import Flask, render_template, request, session, redirect
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from string import ascii_letters, digits
import sqlite3, os, random
from encryption import hashpass_login, decrypt, load_key, encrypt, hashpass, generate_key
from database.database import create_database

#Configuration for the flask app
app = Flask(__name__)
limiter = Limiter(
    app=app, 
    key_func=get_remote_address,
    storage_uri="memory://")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


#Creates the database if it does not exist.
if not os.path.exists("./passwords.db"):
    create_database()

#Used to attempt to connect to the SQLite Database.
def connect_db():
    conn = None
    try:
        conn = sqlite3.connect(os.path.realpath('passwords.db'))
    except sqlite3.Error as e:
        print(e)
    return conn

@app.route("/")
def index():
    #Checks if the user is already logged in.
    if not session.get("name"):
        #Returns the login page if the user is not logged in.
        return render_template("index.html")
    #Otherwise it will fetch the users accounts.
    return redirect("/fetchdata")

#Route used for user registration.
@app.route("/register", methods=["GET", "POST"])
def register():
    #If the user is already logged in it will redirect to the accounts page.
    if session.get("name"):
        return redirect("/fetchdata")

    if request.method == "POST":
        #Attempts to connect to the database.
        conn = connect_db()
        #Sets the cursor
        cursor = conn.cursor()

        #Fetches the following values from the form.
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        confirmpass = request.form.get("confirmpass").strip()

        #Checks if the username is already registered
        try:
            cursor.execute("""
            SELECT username
            FROM users
            WHERE username = ?
            """,[username])
            query = cursor.fetchone();

            #Redirects to the registration page with appropriate error message.
            if(query != None):
                return render_template("register.html", exists=True)

        except sqlite3.Error as e:
            return str(e)

        #Checks if the password fields match.
        if(password != confirmpass):
            return render_template("register.html", match=False)
        
        #If all cases pass it will create the user and store in the database.
        else:
            #Returns the hashed password and the salt
            hashed, salt = hashpass(password)
            #Generates a decryption key for the user.
            generate_key(username)
            #Loads the decryption key
            key = load_key(username)
            
            #List of user information
            user_info = [username, hashed, salt, key]

            #Attempts to insert the user information into the database.
            try:
                cursor.execute("""
                INSERT INTO users VALUES (?,?,?,?)
                """, (user_info[0], user_info[1], user_info[2], user_info[3]))
                conn.commit()
        
            except sqlite3.Error as e:
                return str(e)

            #Closes the connection and redirects to the login page.
            conn.close()
            return render_template("index.html", success=True)

    #Fetches the registration page if method is GET
    if request.method == "GET":
        return render_template("register.html")

#Route used for logging in.
@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        #Connects to the database and sets the cursor
        conn = connect_db()
        cursor = conn.cursor()

        #Form information
        username = request.form.get("username").strip()
        password = request.form.get("password")
        action = request.form.get("act")

        if action == "Login":
            #Checks if the username is in the database
            cursor.execute("""
                SELECT username FROM users
                WHERE username = ?
            """, [username])

            user_result = cursor.fetchone()

            #If it cannot find the user it will return an error message.
            if(user_result == None):
                return render_template("index.html", exists=False)

            #Gets the password and the salt for the corresponding user.
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

            #Checks if the password entered matches the password in the database
            if pass_result[0] != hashpass_login(password, salt[0]):
                return render_template("index.html", failed=True)

            #Sets the session name to the username
            session["name"] = username
            return redirect("/")

#Route used to fetch the user data
@app.route("/fetchdata")
def fetchdata():
    #Connects to the database and sets the cursor.
    conn = connect_db()
    cursor = conn.cursor()
    #Gets the username from the session name.
    username = session["name"]

    #Attempts to load the decryption key.
    try:
        key = load_key(username)
    except:
        return "Key could not be loaded. Make sure its in the root directory."

    #Dictionary of navigation buttons.
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

    #Gets the row id
    cursor.execute(f"""
    SELECT row_id FROM accounts
    WHERE user_id = '{username}'
    """)
    rowid = cursor.fetchall()
    conn.close()

    #Renders the html page with the information from the database
    return render_template("account.html", data=zip(usernames, decrypted, app, web, rowid), nav_btns=nav_btns)

#Used to add an account to the database
@app.route("/addaccount", methods=["GET", "POST"])
def addaccount():
    if request.method == "POST":
        #Gets the username from the session name
        username = session["name"]

        #Attempts to load the decryption key
        try:
            key = load_key(username)
        except:
            return "Key could not be loaded. Make sure its in the root directory."
        
        #Connects to the database and sets the cursor
        conn = connect_db()
        cursor = conn.cursor()

        #Gets the form information
        formusername = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        application = request.form.get("application")
        link = request.form.get("link")

        #Form Validation
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

        #If all cases pass it will encrypt the password with the key.
        encrypted_password = encrypt(password1, key)

        #Tuple of the submitted form information.
        user_info = (formusername, encrypted_password, link, application)
        
        #Attempts to insert the information into the accounts table.
        try:
            cursor.execute(f"""
                INSERT INTO accounts (user_id, username, password, web_link, application)
                VALUES((SELECT username FROM users WHERE username = '{username}'),?,?,?,?)
                """, user_info)
            #Commits to the database
            conn.commit()
        except sqlite3.Error as e:
            return str(e)
        
        #Closes the connection and redirects.
        conn.close()
        return redirect("/")

#Used to remove a password from the accounts table
@app.route("/removepass", methods=["GET", "POST"])
def removepass():
    #Connects to the database and sets the cursor
    conn = connect_db()
    #Used to format the row information when performing queries
    conn.row_factory = lambda cursor,row: row[0]
    cursor = conn.cursor()

    #Sets the username to the session name
    username = session["name"]
    #Gets the row id from the form
    rowid_form = request.form.get("id")

    #Attempts to check if the row belongs to the user and proceeds to delete
    #The row if it does.
    try:
        cursor.execute("""
        SELECT row_id FROM accounts
        WHERE user_id = ?
        """, [username])
        rowid = cursor.fetchall()
        
        if int(rowid_form) in rowid:
            cursor.execute("""
            DELETE FROM accounts
            WHERE row_id = ?
            """, [rowid_form])
        conn.commit()
    except sqlite3.Error as e:
        return str(e)

    #Closes the connection and redirects to /fetchdata
    conn.close()
    return redirect("/fetchdata")

#Route used for changing the master password.
@app.route("/changepass", methods=["GET", "POST"])
def changepass():
    #If the HTTP method is GET it will return html for the form
    if request.method == "GET":
        return """
        <div class="modal-content">
            <button class="close-btn">&times;</button>
            <h2>Change Master Password</h2>
            <form id="change-pass-form" action="/changepass" onsubmit="return changePassValidation()" method="post">
                <div>
                    <label for="currentpass">Password</label><br>
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
        #Connects to the database and sets the cursor
        conn = connect_db()
        cursor = conn.cursor()

        #Sets the username from the session name
        username = session["name"]
        #Gets the form information
        currentpass = request.form.get("currentpass")
        newpass = request.form.get("newpassword")
        confirmpass = request.form.get("confirmpassword")
        
        #Checks if the two password entered in form match.
        if(newpass != confirmpass):
            return "The two passwords do not match."
        
        #gets the password and the salt from the database.
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
        
        #Checks if the password entered it the same as in the database.
        if(hashpass_login(currentpass, salt[0]) != password[0]):
            return "The password you entered does not match your current password."

        #Checks if the password in the database is already the one the user wants to change to.
        elif(hashpass_login(currentpass, salt[0]) == password[0]):
            return "Cannot change password to your current password."

        #Otherwise it will attempt to to change the password in the database
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

        #Closes the connection and logs the user out of their account
        conn.close()
        session["name"] = None
        #Redirects to the login page.
        return redirect("/")

#Route used to delete the master account
@app.route("/deleteacc", methods=["GET", "POST"])
def deleteacc():
    #If the HTTP method is GET it will return the html for the form.
    if request.method == "GET":
        return """
        <div class="modal-content">
            <button class="close-btn">&times;</button>
            <h2>Delete Master Account</h2>
            <form id="delete-acc-form" action="/deleteacc" onsubmit="return formValidation()" method="post">
                <div>
                    <label for="password">Password</label><br>
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
        #Connects to the database and sets the cursor
        conn = connect_db()
        cursor = conn.cursor()

        #Gets the form information
        username = session["name"]
        password = request.form.get("password")
        confirmpass = request.form.get("confirmpassword")

        #Checks if the two password fields match.
        if(password != confirmpass): 
            return "Password fields do not match."

        #Gets the password from the database.
        cursor.execute("""
        SELECT password FROM users
        WHERE username = ?
        """, [username])
        dbpassword = cursor.fetchone()

        #Gets the salt from the database.
        cursor.execute("""
        SELECT salt FROM users
        WHERE username = ?
        """, [username])
        salt = cursor.fetchone()
        
        #Checks if the password entered matches the password in the database.
        if(hashpass_login(password, salt[0]) != dbpassword[0]):
            return "Password entered does not match the account password."
        
        #Attempts to remove all records for the corresponding user in 
        #the accounts table, then removes the user itself from the users table.
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
            #Deletes the decryption key.
            os.remove(f"{username}.key")
        except sqlite3.Error as e:
            return str(e)
        
        #Closes the connection and removes the session name
        conn.close()
        session["name"] = None
        #Redirects to the login page.
        return redirect("/")

@app.route("/genpass")
@limiter.limit("10 per minute")
def genpass():
    if request.method == "GET":
        password = ""
        all_chars = ascii_letters + digits + "!#$%*@"
        for i in range(25):
            password += random.choice(all_chars)
        return password

#Used to log the user out their account.
@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")

# Runs the server on any ip and port is set to 8080 (change to 0 to auto pick),
# debugging set to true while in development.
# if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=8080, ssl_context="adhoc")