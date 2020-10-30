from os.path import isfile
from os import system
from time import sleep
import sqlite3 as sql
from sqlite3 import Error
from cryptography.fernet import Fernet


class Setup:
    @classmethod
    def __init__(cls):
        # Checks if the Database.db file exists or not.
        if os.path.isfile('Database.db'):
            database_exist = True
        else:
            database_exist = False

        try:
            cls.con = sql.connect('Database.db')
        except Error:
            print(Error)
            sleep(3)
            quit()

        # If the Database.db file doesn't exist it creates one
        cls.c = cls.con.cursor()
        if not database_exist:
            cls.c.execute("CREATE TABLE USERS(userid, username, password, key)")
            cls.con.commit()

    @classmethod
    def create_new_user(cls):
        c = cls.con.cursor()

        # Clear the screen
        system('cls')

        key = Fernet.generate_key()
        f = Fernet(key)

        print("enter a username you won't forget")
        username = input()
        while True:
            system('cls')
            print("enter a password you won't forget")
            password = input()
            print("Re-enter the password")
            if password == input():
                break
            else:
                print("The passwords do not match please try again")

        # Encrypts username and password using the cryptography library
        username = f.encrypt(username.encode())
        password = f.encrypt(password.encode())

        # Checks the number of users to give it a name like USER2, USER3 etc
        number = len(c.execute("SELECT userid FROM USERS").fetchall()) + 1
        if c.execute("SELECT userid FROM USERS").fetchone() == "USER1":
            number -= 1

        # Inserts the user id, username, password and the key used to encrypt the username and password
        c.execute("INSERT INTO USERS VALUES(?, ?, ?, ?)", ("USER" + str(number), username, password, key))

        print("Your username and password has been encrypted and stored in your database\n")

        # Creates a new table for the new user
        c.execute("CREATE TABLE " + "USER" + str(number) + "(account, username, password, key)")

        # Saves the changes made to the sql database
        cls.con.commit()

        print("Your user id is USER" + str(number) +
              "\nIt is not necessary to remember this")
        sleep(3)

        cls.create_new_user_ask()

    @classmethod
    def create_new_user_ask(cls):
        while True:
            system('cls')
            print("\nDo you want to create a new user?   y/n\n")
            choice = input()

            if choice == 'y':
                cls.create_new_user()
            elif choice == 'n':
                quit()
            else:
                print("Wrong choice!!")

    @classmethod
    def connect(cls):
        # Prints the Readme file as credits and instructions
        with open('README.md') as file:
            file_data = file.read()
            print(file_data)
            file.close()

        print("\n\n\n\n\nEnter to go to the next page")
        input()
        system('cls')  # Clears the screen


def setup():
    obj = Setup()

    obj.connect()
    obj.create_new_user_ask()
