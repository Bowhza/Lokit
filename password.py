#------------------------------------------------------
# LOKIT - Python Password Manager (Rewritten)
#------------------------------------------------------
# This application uses cryptography, sqlite, and 
# bcrypt libraries that are required for the program
# to run.
#------------------------------------------------------
# Created by: https://github.com/Bowhza
# Last Updated: February 27, 2023
#------------------------------------------------------

#Importing Files and Libraries
from string import ascii_letters, digits
from encryption import encrypt, decrypt, load_key, generate_key, hashpass, hashpass_login
from database.database import create_database
import random
import sqlite3
import os

#This is the default file name where the passwords will be stored.
file = "passwords.db"

#This gets the current directory of the python file.
directory = os.getcwd()

#Function that will create the database if it does not already exist
def check_db():
    if not os.path.exists(f'{directory}/{file}'):
        print("DATABASE DOES NOT EXIST. CREATING THE DATABASE...")
        create_database()
    else:
        print("DATABASE EXISTS. RUNNING APPLICATION...")

#This will generate the password based on the user specified length.
def generate_pass(length):
    password = ""
    all_chars = ascii_letters + digits + "!#$%*@"
    for i in range(length):
        password += random.choice(all_chars)
    #Displays the password and returns it.
    print("Your password is: " + password)
    return password

#This function creates a user for the password manager
def create_user(database, cursor):
    valid_user = False
    valid_pass = False
    user_info = []
    
    while not valid_user:
        user_name = str(input("Enter a username: "))
        #Checks if the username exists in the database
        cursor.execute("""
            SELECT username FROM users
            WHERE username = ?
        """, [user_name])
        result = cursor.fetchone()
        #If it does then display the error message.
        if result != None:
            print("USERNAME IS ALREADY TAKEN, PLEASE PICK ANOTHER ONE.")
        #Otherwise add the username to the list
        else:
            valid_user = True
            user_info.append(user_name)
    #While loop to get the user to enter an account password
    while not valid_pass:
        user_pass = str(input("Enter a password: "))
        if user_pass != str(input("Confirm Password: ")):
            print("PASSWORDS DO NOT MATCH, TRY AGAIN.")
        else:
            valid_pass = True
            #Creates the hashed password with the salt and returns both
            hashed, salt = hashpass(user_pass)
            #Adds the information to the list
            user_info.append(hashed)
            user_info.append(salt)

            #Generates a decryption key
            generate_key(user_name)
            #Loads the key and appends to the list
            key = load_key(user_name)
            user_info.append(key)

            #Inserts the new account into the users database
            cursor.execute("""
            INSERT INTO users VALUES (?,?,?,?)
            """, (user_info[0], user_info[1], user_info[2], user_info[3]))
            database.commit()

            #Displays important message about the decryption key.
            print(f"IMPORTANT: An encryption key was generated for your user {user_name}.key that will be used" +
                  "\nto encrypt and decrypt the passwords stored in the database. \nIF THE KEY IS LOST, THE PASSWORDS WILL BE UNACCESSABLE.")

#This function will log a user into the password manager database if user exists.
def login_user(database, cursor):
    user_name = str(input("Enter your username: "))

    #Checks it the username exists in the database of users
    cursor.execute("""
        SELECT username FROM users
        WHERE username = ?
    """, [user_name])
    result = cursor.fetchone()

    #If it does not exists then it will display a message.
    if result == None:
        print("USER DOES NOT EXISTS. PLEASE REGISTER AN ACCOUNT.")
    
    #Otherwise it will prompt the user to login.
    else:
        password = str(input("Enter your password: "))
        #Fetches the hashed password from the database
        cursor.execute("""
        SELECT password FROM users
        WHERE username = ?
        """, [user_name])
        result = cursor.fetchone()
        #Fetches the salt of the password from the database
        cursor.execute("""
            SELECT salt FROM users
            WHERE username = ?
        """, [user_name])
        salt = cursor.fetchone()
        
        #Checks if the passwords match
        if result[0] != hashpass_login(password, salt[0]):
            print("THE PASSWORD IS INCORRECT. EXITING TO MENU.")
        #If they match then the submenu will display for the user
        else:
            option = sub_menu(user_name)
            if option == 1:
                #Shows the passwords
                show_passwords(user_name, cursor)
            elif option == 2:
                #Allows the user to enter new data
                user_data = create_entry(load_key(user_name))
                #Inserts and commits the data to the database
                cursor.execute(f"""
                INSERT INTO accounts VALUES((SELECT username FROM users WHERE username = '{user_name}'),?,?,?,?)
                """, user_data)
                database.commit()

#This is the menu where it will ask if the user want to generate or view saved passwords.
def main_menu():
    print("""
    #--------------------------------#
    # LOKIT - LOCAL PASSWORD MANAGER #
    # (1) LOGIN                      #
    # (2) REGISTER ACCOUNT           #
    # -------------------------------#
    """)
    options = int(input("OPTION > "))
    while options != 1 and options != 2:
        options = int(input("Invalid input. Try again: "))
    print()

    return options

#Sub menu that will ask the user if they want to retrieve or add new password to the database
def sub_menu(username):
    print(f"""
    #--------------------------------#
    # LOKIT - LOCAL PASSWORD MANAGER #      
    # (1) RETRIEVE PASSWORDS         #
    # (2) ADD NEW PASSWORDS          #
    # -------------------------------#
    """)
    print(f"LOGGED IN AS: {username}")
    options = int(input("OPTION > "))
    while options != 1 and options != 2:
        options = int(input("Invalid input. Try again: "))
    print()

    return options

#Function that creates and inserts a new entry to the database
def create_entry(key):
    valid_pass = False
    while not valid_pass:
        user_pass = str(input("Enter a password: "))
        if user_pass != str(input("Confirm Password: ")):
            print("PASSWORDS DO NOT MATCH, TRY AGAIN.")
        else:
            valid_pass = True
    #All entries that are inserted into the accounts table
    encrypted_password = encrypt(user_pass, key)
    username = str(input("Enter a username for this account: "))
    application = str(input("Enter an application where it will be used: "))
    web_link = str(input("Enter a link for the site (if applicable): "))
    #Returns a tuple of the data that will be inserted
    return (username, encrypted_password, web_link, application)

#Displays the passwords from the database.
def show_passwords(username, cursor):
    try:
        key = load_key(username)
    except:
        print("THE KEY COULD NOT BE RETRIEVED, MAKE SURE ITS IN THE ROOT DIRECTORY OF THE LOKIT FOLDER.")
        return
    
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

    #Displays all of the information to the console window
    print("HERE ARE YOUR ACCOUNTS:")
    for (username, password, application, website) in zip(usernames, decrypted, app, web):
        print(f"USERNAME: {username[0]} | PASSWORD: {password.decode()} | APPLICATION: {application[0]} | WEBSITE: {website[0]}")


#This is the main function that takes in all the other helper functions.
def main():
    check_db()
    db = sqlite3.connect("passwords.db")
    cursor = db.cursor()

    running = True

    while running:
        choice = main_menu()
        if choice == 1:
            login_user(db, cursor)
        if choice == 2:
            create_user(db ,cursor)


#This will run the program.
if __name__ == "__main__":
    main()  