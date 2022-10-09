#------------------------------------------------------
# Password generator and password manager with
# file encryption.
#------------------------------------------------------
# Make sure to uncomment the "generate_key()" 
# function call in before you run this program 
# for the first time to generate a key. Keep the 
# key safe otherwise the file will be lost forverver.
#------------------------------------------------------
# Created by: https://github.com/Bowhza
# Last Updated: March 7, 2022
#------------------------------------------------------

from string import ascii_letters, digits
from encryption import encrypt, decrypt, load_key, generate_key
import random
import os

#Uncomment this function and run it once to generate the key.
#After you can remove or comment it out again.
#generate_key()

#This will load the key and assign it to the key variable
key = load_key()

#This is the default file name where the passwords will be stored.
#You can change the name of the file and uncomment the encrypt()
#function at the bottom of this python file and run it once.
file = "passwords.txt"

#This gets the current directory of the python file.
directory = os.getcwd()

#THis function get the user specified password length.
def get_length():
    #Error checks user input to see if it is an integer.
    while True:
        try:
            length = int(input("Enter password length. (Min: 10 | Max: 100): "))
        except:
            print("Not a valid password length, please try again.\n")
            continue
        else:
            break
    #This makes sure that the passord is within range.
    if length > 100:
        length = 100
    elif length < 10:
        length = 10
    return length

#This will generate the password based on the user specified length.
def generate_pass(length):
    password = ""
    all_chars = ascii_letters + digits + "!#$%*@"
    for i in range(length):
        password += random.choice(all_chars)
    #Displays the password and returns it.
    print("Your password is: " + password)
    return password


#This will prompt the user if they want to save the password to a file.
def save_file(password, key):
    save = input("\nWould you like to save this password (y/n): ").lower()
    while save != "y" and save != "n":
        save = input("Invalid input. Try again. (y/n): ").lower()
    
    #If yes it will try to decrypt the file.
    if save == "y":
        run = True
        try:
            decrypt(file, key)
        #If the key is invalid it will stop the program.
        except:
            print("Key is invalid. Unable to save password.")
            run = False

        #If the key is valid and the user selected "y" then it will proceed with saving the password.
        while run == True:
            #prompts the user for the place where the password will be used and their email (optional).
            name = input("Enter a name for the password ex. Discord, Facebook, etc.: ")
            email = input("Enter email that will be used with the password. (Can be left empty): ")
            if email == "":
                total = name + " | " + password + "\n"
            else:
                total = name + " | " + email + " | " + password + "\n"

            #opens the file, saves the password, and the closes it.
            save_file = open(file, "a")
            save_file.write(total)
            save_file.close()

            print("\nPassword saved to '" + file + "' in this directory: " + directory)
            print("NOTE: The text file is encrypted and will require the generated key to read the contents.")
            print("WARNING! If the key is lost the contents of the file will become unrecoverable.")

            #Then it encrypts the file again.
            encrypt(file, key)
            break
    else:
        print("Password was not saved.")

#This is the menu where it will ask if the user want to generate or view saved passwords.
def menu():
    options = int(input("(1) Generate Password | (2) View saved passwords: "))
    while options != 1 and options != 2:
        options = int(input("Invalid input. Try again: "))
    print()

    if options == 1:
        return 1
    else:
        return 2

#This function will display the saved passwords in the terminal/
def read_passwords(file, key):
    #Tries to decrypt the file if it has not been already.
    try:
        decrypt(file, key)
        print("Here are your passwords:\n")
        
        #Then if will open the file and print out each password.
        password_file = open(file, "r")
        file_line = password_file.readline()
        while file_line:
            print(file_line)
            file_line = password_file.readline()
    
        #closes the file and encrypts it.
        password_file.close()   
        encrypt(file, key)
    except:
        print("Key is Invalid.")
    

#This is the main function that takes in all the other helper functions.
def main():
    print("\t-= Password Generator and Manager =-")
    choice = menu()
    if choice == 1:
        length = get_length()
        password = generate_pass(length)
        save_file(password, key)
    elif choice == 2:
        read_passwords(file, key)

#This will run the program.
if __name__ == "__main__":
    #Run this function once if you changed the default saved passwords file name.
    #encrypt(file, key)
    main()