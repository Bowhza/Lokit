from cryptography.fernet import Fernet
import bcrypt
 
#This fucntion generates the key and stores it in a key file. 
def generate_key(username):
    key = Fernet.generate_key()
    with open(f"./keys/{username}.key", "wb") as key_file:
        key_file.write(key)

#This functon reads the key from the key file and returns it.
def load_key(keyname):
    return open(f"./keys/{keyname}.key", "rb").read()

#This is the function that encrypts the password
def encrypt(password, key):
    #It takes in the password and key and encrypts the data.
    fernet = Fernet(key)

    encrypted_data = fernet.encrypt(password.encode())
    return encrypted_data

def decrypt(password, key):
    fernet = Fernet(key)

    #The decrypted data replaces the encrypted data.
    decrypted_data = fernet.decrypt(password)
    return decrypted_data

#Hashes the password with a random salt
def hashpass(password):
    password = password.encode("ascii")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed, salt

#Checks if passwords match on login
def hashpass_login(password, salt):
    password = password.encode("ascii")
    hashed = bcrypt.hashpw(password, salt)
    return hashed