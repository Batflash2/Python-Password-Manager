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
            os.system('cls')
            print("1: Login\n"
                  "2: Create new user\n"
                  "3: Check number of users\n"
                  "q: Quit the Password Manager"
                  "\nEnter 1 or 2\n")

            choice = input()
            if choice == '1':
                cls.login()
                break
            elif choice == '2':
                setup()
                break
            elif choice == '3':
                cls.check_number_of_users()
            elif choice == 'q':
                quit()
            else:
                print("Error wrong choice!!")
                sleep(3)

    @classmethod
    def login(cls):
        while True:
            print("Enter your username")
            username = input()
            print("Enter your password")
            password = input()

            # variable to check if the username and password matches to that of any of the stored user credentials
            success = False
            rows = cls.c.execute("SELECT * FROM USERS").fetchall()
            for row in rows:
                user_id, decrypted_username, decrypted_password = cls.decrypt_username_and_password(row)
                if username == decrypted_username and password == decrypted_password:
                    success = True
                    cls.user_id = user_id
                    del (user_id, username, password, decrypted_username, decrypted_password)
                    break

            if not success:
                print("Error username and password do not match")
            else:
                print("Successfully logged in as " + cls.user_id)
                break
        cls.second_menu()

    @classmethod
    def second_menu(cls):
        while True:
            os.system('cls')
            print("Do you want to:\n"
                  "1: Add an account's credentials\n"
                  "2: Look through the data\n"
                  "3: Remove an account's credentials\n"
                  "q: Quit")
            choice = input()
            if choice == '1':
                cls.add_account_credentials()
            elif choice == '2':
                cls.display_all_user_credentials()
            elif choice == '3':
                cls.remove_account_credentials()
            elif choice == 'q':
                quit()
            else:
                print("ERROR: Wrong choice")
                sleep(3)

    @classmethod
    def add_account_credentials(cls):
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

        # Delete sensitive data
        del (username, password)

        cls.c.execute("INSERT INTO " + cls.user_id + " VALUES(?, ?, ?, ?)",
                  (account_name, encrypted_username, encrypted_password, key))
        cls.con.commit()

    @classmethod
    def remove_account_credentials(cls):
        pass

    @classmethod
    def display_all_user_credentials(cls):
        print(cls.user_id)
        rows = cls.c.execute("SELECT * FROM " + cls.user_id).fetchall()
        if rows:
            print("{:<15} {:<15} {:<15}".format("ACCOUNT", "USERNAME", "PASSWORD"))
            print(rows)
            for row in rows:
                account, decrypted_username, decrypted_password = cls.decrypt_username_and_password(row)
                print("{:<15} {:<15} {:<15}".format(account, decrypted_username, decrypted_password))
                print("\n\n 10 second delay before the data disappears")
                sleep(10)
            del (rows, row, decrypted_username, decrypted_password)

        else:
            print("\n\n\n\nHE DATA YOU ARE LOOKING FOR DOES NOT EXIST\n\n\n")

    @classmethod
    def check_number_of_users(cls):
        user_ids = cls.c.execute("SELECT users FROM USERS").fetchall()
        print(user_ids)
        print("There are " + str(len(user_ids)) + " users")

    @classmethod
    def decrypt_username_and_password(cls, row):
        user_id_or_account_name, stored_username, stored_password, stored_key = row

        f = Fernet(stored_key)
        decrypted_username = f.decrypt(stored_username).decode()
        decrypted_password = f.decrypt(stored_password).decode()

        return user_id_or_account_name, decrypted_username, decrypted_password


if __name__ == '__main__':
    obj = PasswordManager()

    obj.main_menu()
