import sqlite3

def create_database():
    db = sqlite3.connect("passwords.db")
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS users;")

    cursor.execute("""
        CREATE TABLE users(
            username varchar(50) unique,
            password varchar(100),
            salt varchar(100),
            encryption_key varchar(255)
        );
    """)


    cursor.execute("DROP TABLE IF EXISTS accounts;")

    cursor.execute("""
        CREATE TABLE accounts(
            row_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id varchar(50),
            username varchar(255) not null,
            password binary(255) not null,
            web_link varchar(255),
            application varchar(100) not null,
            FOREIGN KEY(user_id) REFERENCES users(username)
        );
    """)

    db.commit()
    db.close()