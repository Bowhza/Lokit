# Lokit

Lokit is a password generator and password vault project made in python using bcrypt, cryptography, sqlite3, and flask. The Lokit server is meant to run on the local network.

## To-Do List

### Recently Added

#### April 29, 2023
- [x] Added additional CSS styling and Lokit logo.
- [x] Added confirmation prompt when deleting a password entry.
- [x] Made Layout more responsive for mobile.

#### April 30, 2023
- [x] Hide passwords in account blocks by default and add a button to make it visible.
- [x] Add feature to change the account password.
- [x] Add feature to be able to delete the master account.
- [x] Add "create new account" functionality.

#### May 1, 2023
- [x] Write better code documentation.
- [x] Create button that will generate a random password a user can use for their accounts.
- [x] Add ability to copy password to the clipboard.<br>
- [x] Updated readme.md and requirements.txt

#### December 6, 2024
- [x] Added a docker compose file to run the application in a container.
- [x] Added a .gitignore file.

> [!Important]
> The ability to copy text to the clipboard is only available over HTTPS. 
> The application uses a dummy certificate to achieve this functionality and therefore will say that the website is unsecure. 
> The user can choose to modify the application to use their own SSL Certificate.

## How to run the application

1. Install Docker and Docker Compose on your machine.
2. Clone the repository.
3. Navigate to the root directory of the project, and open it in your terminal.
4. Run the following command to build the docker image and start the container.
```bash
docker-compose up --build
```
5. You can now access the application on `https://{IP Address}:8080` where the "IP Address" is the machine running the container.

## Authors

- [@Bowhza](https://www.github.com/Bowhza)