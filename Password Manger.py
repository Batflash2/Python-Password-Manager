from os.path import isfile
from os import system
from time import sleep
import sqlite3 as sql
from sqlite3 import Error
from cryptography.fernet import Fernet
from Setup import setup


class PasswordManager:
    @classmethod
    def __init__(cls):
        if not isfile('Database.db'):
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
            system('cls')
            print("1: Login\n"
                  "2: Create new user\n"
                  "3: Check number of users\n"
                  "q: Quit the Password Manager")

            choice = input()
            if choice == '1':
                cls.login()
            elif choice == '2':
                setup()
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
            system('cls')
            print("Enter your username")
            username = input()
            print("Enter your password")
            password = input()

            # variable to check if the username and password matches to that of any of the stored user credentials
            success = False
            rows = cls.c.execute("SELECT * FROM USERS").fetchall()
            for row in rows:
                user_id, name, decrypted_username, decrypted_password = decrypt_username_and_password(row)
                if username == decrypted_username and password == decrypted_password:
                    success = True
                    cls.user_id = user_id
                    cls.decrypted_password = decrypted_password
                    break

            if not success:
                print("Error username and password do not match")
            else:
                print("Successfully logged in as " + cls.user_id)
                sleep(2)
                break
        cls.user_menu()

    @classmethod
    def user_menu(cls):
        while True:
            system('cls')
            print("Do you want to:\n"
                  "1: Add an account's credentials\n"
                  "2: Look through the data\n"
                  "3: Change user password\n"
                  "4: Remove an account's credentials\n"
                  "5: Change account password\n"
                  "6: Remove user\n"
                  "7: Logout\n"
                  "q: Quit")

            choice = input()

            if choice == '1':
                cls.add_account_credentials()
            elif choice == '2':
                cls.display_all_user_credentials()
            elif choice == '3':
                cls.change_user_password()
            elif choice == '4':
                cls.remove_account_credentials()
            elif choice == '5':
                cls.change_account_password()
            elif choice == '6':
                cls.remove_user()
            elif choice == '7':
                break
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

        account_id = len(cls.c.execute("SELECT account_id FROM " + cls.user_id).fetchall()) + 1
        if cls.c.execute("SELECT account_id FROM " + cls.user_id).fetchone() == "1":
            account_id -= 1

        cls.c.execute("INSERT INTO " + cls.user_id + " VALUES(?, ?, ?, ?, ?)",
                      (account_id, account_name, encrypted_username, encrypted_password, key))
        cls.con.commit()

    # Function to change the password of the user currently logged in
    @classmethod
    def change_user_password(cls):
        while True:
            print("Enter the new password:")
            new_password = input()
            print("Re-enter the password:")
            if new_password == input():
                stored_key = cls.c.execute("SELECT key FROM USERS WHERE userid = ?", (cls.user_id,)).fetchone()
                stored_key = str(stored_key)[3:-3].encode()
                f = Fernet(stored_key)
                encrypted_new_password = f.encrypt(new_password.encode())
                cls.c.execute("UPDATE USERS SET password = ? WHERE userid = ?",
                              (encrypted_new_password, cls.user_id,))
                cls.con.commit()
                break
            else:
                print("The passwords do not match please try again")
                sleep(3)

    # Change passwords for the accounts that have already been entered
    @classmethod
    def change_account_password(cls):
        while True:
            system('cls')
            cls.display_all_user_credentials()

            print("Enter the account id of the account password you want to change")
            account_id = int(input())

            max_account_id = len(cls.c.execute("SELECT account_id FROM " + cls.user_id).fetchall()) + 1
            if cls.c.execute("SELECT account_id FROM " + cls.user_id).fetchone() == "1":
                max_account_id -= 1

            # To check if the password has been successfully updated or not
            done = False

            # To check if the id entered by the user is within the range or not
            if 0 < account_id <= max_account_id:
                while True:
                    system('cls')
                    if cls.confirm_user() == "confirmed":
                        print("You are about to change the password for the following account")
                        cls.display_one_user_credential(account_id)
                        print("Enter the new password:")
                        new_password = input()
                        print("Re-enter the password:")
                        if new_password == input():
                            stored_key = cls.c.execute("SELECT key FROM " + cls.user_id + " WHERE account_id = ?",
                                                       (account_id,)).fetchone()
                            stored_key = str(stored_key)[3:-3].encode()
                            f = Fernet(stored_key)
                            encrypted_new_password = f.encrypt(new_password.encode())
                            cls.c.execute("UPDATE " + cls.user_id + " SET password = ? WHERE account_id = ?",
                                          (encrypted_new_password, account_id,))
                            cls.con.commit()
                            done = True
                            break
                        else:
                            print("The passwords do not match please try again")
                            sleep(3)
                    else:
                        done = True
                        break
            else:
                print("Error: Wrong input")
                sleep(2)

            # Exit the loop if the password has been successfully updated
            if done:
                break

    # To remove an account credential when it is no longer required
    @classmethod
    def remove_account_credentials(cls):
        cls.display_all_user_credentials()
        print("Enter the account_id")
        account_id = input()

        while True:
            system('cls')
            print("Are you sure you want to delete the credentials for this account?   y/n")
            cls.display_one_user_credential(account_id)
            choice = input()
            if choice == "y" or choice == "Y":
                if cls.confirm_user() == "confirmed":
                    cls.c.execute("DELETE FROM " + cls.user_id + " WHERE account_id = " + str(account_id))
                    print("The credentials have been deleted")
                    cls.rearrange_accounts(int(account_id))
                    break
                else:
                    break
            elif choice == "n" or choice == "N":
                break
            else:
                print("Error: Wrong option. Try again")

        cls.con.commit()

    @classmethod
    def remove_user(cls):
        pass

    # To rearrange the accounts after an account has been removed since there is a number gap
    @classmethod
    def rearrange_accounts(cls, deleted_account_id):
        for i in range(deleted_account_id, len(cls.c.execute("SELECT account_id FROM " + cls.user_id).fetchall()) + 2):
            cls.c.execute("UPDATE " + cls.user_id + " SET account_id = ? WHERE account_id = ?", (i - 1, i))
        cls.con.commit()

    @classmethod
    def confirm_user(cls):
        while True:
            print("Enter your user password or just press enter to exit")
            password = input()
            if password == cls.decrypted_password:
                return "confirmed"
            elif password == "":
                return "exit"
            else:
                print("Error the password does not match. Please try again")
                sleep(2)

    @classmethod
    def copy_to_clipboard(cls):
        pass

    @classmethod
    def display_one_user_credential(cls, account_id):
        row = cls.c.execute("SELECT * FROM " + cls.user_id + " WHERE account_id = " + str(account_id)).fetchone()
        print("\n")
        print("{:<5} {:<15} {:<15} {:<15}".format("ID", "ACCOUNT", "USERNAME", "PASSWORD"))
        account_id, account, decrypted_username, decrypted_password = decrypt_username_and_password(row)
        print("{:<5} {:<15} {:<15} {:<15}".format(account_id, account, decrypted_username, decrypted_password))

    @classmethod
    def display_all_user_credentials(cls):
        print(cls.user_id)
        rows = cls.c.execute("SELECT * FROM " + cls.user_id).fetchall()
        if rows:
            print("{:<5} {:<15} {:<15} {:<15}".format("ID", "ACCOUNT", "USERNAME", "PASSWORD"))
            for row in rows:
                account_id, account, decrypted_username, decrypted_password = decrypt_username_and_password(row)
                print("{:<5} {:<15} {:<15} {:<15}".format(account_id, account, decrypted_username, decrypted_password))

            print("\n\n Press enter to proceed")
            input()

        else:
            print("\n\n\n\nTHE DATA YOU ARE LOOKING FOR DOES NOT EXIST\n\n\n")
            sleep(3)

    @classmethod
    def check_number_of_users(cls):
        user_ids = cls.c.execute("SELECT userid FROM USERS").fetchall()
        print("\n\nThere are " + str(len(user_ids)) + " users\n\n")

        if len(user_ids) > 0:
            rows = cls.c.execute("SELECT * FROM USERS")
            print("{:<10} {:<15}".format("USER ID", "NAME"))
            for row in rows:
                user_id, name, decrypted_username, decrypted_password = decrypt_username_and_password(row)
                print("{:<10} {:<15}".format(user_id, name))

        print("\n\n")
        print("Click enter to continue")
        input()


def decrypt_username_and_password(row):
    user_id_or_account_id, account, stored_username, stored_password, stored_key = row

    f = Fernet(stored_key)
    decrypted_username = f.decrypt(stored_username).decode()
    decrypted_password = f.decrypt(stored_password).decode()

    return user_id_or_account_id, account, decrypted_username, decrypted_password


if __name__ == '__main__':
    obj = PasswordManager()

    obj.main_menu()
