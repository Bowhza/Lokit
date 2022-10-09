from cryptography.fernet import Fernet
 
#This fucntion generates the key and stores it in a key file. 
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

#This functon reads the key from the key file and returns it.
def load_key():
    return open("key.key", "rb").read()

#This is the function that encrypts the file.
def encrypt(filename, key):
    #It takes in the filename and key and encrypts the data.
    fernet = Fernet(key)
    with open(filename, "rb") as file:
        file_data = file.read()

    #The encrypted data replaces the decrypted data.
    encrypted_data = fernet.encrypt(file_data)
    with open(filename, "wb") as file:
        file.write(encrypted_data)

#This is the function that decrypts the file.
def decrypt(filename, key):
    #It takes in the filename and key and decrypts the data.
    fernet = Fernet(key)
    with open(filename, "rb") as file:
        encrypted_data = file.read()

    #The decrypted data replaces the encrypted data.
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(filename, "wb") as file:
        file.write(decrypted_data)