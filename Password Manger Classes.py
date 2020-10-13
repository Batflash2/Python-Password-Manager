import os.path
from time import sleep
import sqlite3 as sql
from sqlite3 import Error
from cryptography.fernet import Fernet
from Setup_with_Classes import setup


class PasswordManager:
    @classmethod
    def __init__(cls):
        if not os.path.isfile('Database.db'):
            print("Error the database file was not found!!\n\n"
                  "Creating new Database file")
            sleep(3)

            setup()

        try:
            cls.con = sql.connect('Database.db')
        except Error:
            print(Error)
            sleep(3)
            quit()

        cls.c = cls.con.cursor()

    @classmethod
    def main_menu(cls):
        while True:
            print("1: Login"
                  "2: Create new user"
                  "3: Check number of users"
                  "\nEnter 1 or 2")

            choice = input()
            if choice == '1':
                cls.login()
                break
            elif choice == '2':
                setup()
                break
            else:
                print("Error wrong choice!!")

    @classmethod
    def login(cls):
        while True:
            print("Enter your username")
            username = input()
            print("Enter your password")
            password = input()

            # Get the number of users to loop through all and check the credentials
            c = con.cursor()
            count = len(c.execute("SELECT * FROM USERS").fetchall())

            stored_usernames = c.execute("SELECT username FROM USERS").fetchall()
            stored_passwords = c.execute("SELECT password FROM USERS").fetchall()
            stored_keys = c.execute("SELECT key FROM USERS").fetchall()

            success = False
            for user_id in range(count):
                f = Fernet(stored_keys[user_id])
                encrypted_username = f.encrypt(username.encode())
                encrypted_password = f.encrypt(password.encode())
                if encrypted_username == stored_usernames[user_id] and encrypted_password == stored_passwords[user_id]:
                    success = True
                    break

            if not success:
                print("Error username and password do not match")
            else:
                print("Successfully logged in as USER" + str(user_id + 1))
                break

    def second_menu(self):
        while True:
            print("Do you want to:"
                  "1: Add an account's credentials"
                  "2: Look through the data"
                  "3: Remove an account's credentials")
            choice = input()

    def add_account_credentials(self):
        print("Enter the name of the account you want to store")
        account_name = input()
        print("enter the username of the account you want to store")
        username = input()
        print("enter a password of the account you want to store")
        password = input()

        key = Fernet.generate_key()
        f = Fernet(key)
        encrypted_username = f.encrypt(username.encode())
        encrypted_password = f.encrypt(password.encode())

        c = con.cursor()
        c.execute("INSERT INTO USER" + str(self.user_id) + "VALUES(?, ?, ?, ?)",
                  (account_name, encrypted_username, encrypted_password, key))

    def remove_account_credentials(self):
        pass


if __name__ == '__main__':
    pass
