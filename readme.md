# Lokit

Lokit is a password generator and password vault project made in python using bcrypt, cryptography, sqlite3, and flask. This is the GUI update test branch that will be merged to main in the future.

## To-Do List

### Recently Added

#### April 29, 2023
- [x] Added additional CSS styling and Lokit logo.
- [x] Added confirmation prompt when deleting a password entry.
- [x] Made Layout more responsive for mobile.

#### April 30, 2023
- [x] Hide passwords in account blocks by default and add a button to make it visible.
- [x] Add feature to change the account password.

### Future Additions

- [ ] Add feature to be able to delete the master account.
- [ ] Create button that will generate a random password a user can use for their accounts.
- [ ] Add ability to copy username and/or password to clipboard.
- [ ] Add "create new account" functionality.
- [ ] Dark Mode? 🌑

**More items may be added to this list in the future.**

## Dependencies

**The following libraries are required for the application to run:**
- Flask
- Flask-Session
- SQLite
- BCrypt
- Cryptography

**You can use the provided requirements file in the root directory.**<br>

```
pip install -r requirements.txt
```

## How To Run

1. Run the app.py script to start the flask server.

2. Then <kbd>CTRL</kbd> + <kbd>Right Mouse Click</kbd> on the 'Running on' link in the terminal.

3. The Web App should now have opened in your default browser.

**Note: The Flask server is running in debug mode while these updates are still being worked on.**

## Authors

- [@Bowhza](https://www.github.com/Bowhza)