import getpass
import json
import time
import hashlib
from colorama import Fore, Style
from common_functions import clear_screen, log_action
from pymongo import MongoClient
from config import mongodb_uri


MAX_ATTEMPTS = 2

# Connect to MongoDB
uri = mongodb_uri
client = MongoClient(uri)
db = client['animal_rescue']
users_collection = db['users']

def sudo_user():
    # Continuous loop for sudo user authentication
    attempts = 0 

    clear_screen()

    while attempts < MAX_ATTEMPTS:
        print(Fore.LIGHTMAGENTA_EX + "\n👤 Sudo Login 👤" + Style.RESET_ALL)
        print("\nPlease enter your credentials")
        username = input("\nEnter your username: ")
        password = getpass.getpass("Enter your password: ")

        user = users_collection.find_one({'username': username})

        if user:
                stored_password = user['hashed_password']
                salt = bytes.fromhex(user['salt'])

                # Hash the entered password with the stored salt
                entered_password_hash = hashlib.sha256(password.encode('utf-8') + salt).hexdigest()

                if stored_password == entered_password_hash:
                    user_level = user['level']
                    # Throw error if user is logging in with ADMIN account
                    if username == "ADMIN":
                        print("\nNot a valid username")
                        clear_screen()
                        sudo_user()
                        return username
                    
                    # Notify about user verification
                    elif user_level >= 1:        
                            print(Fore.GREEN +"\nUser Verified..." + Style.RESET_ALL)
                            time.sleep(2)
                            clear_screen()
                            return user

                    # Notify insufficient clearance
                    else:
                        print(Fore.RED + "\nYou do not have clearance to do this." + Style.RESET_ALL)
                        time.sleep(1)
                        print(Fore.RED + "\nADMIN user will be alerted." + Style.RESET_ALL)
                        time.sleep(1)
                        print(Fore.RED + "\nExiting..." + Style.RESET_ALL)
                        time.sleep(1)

                        # Log user's username and add it to audit log
                        log_action(username, f"Tried to access without clearance")
                        exit()
                
                # Notify about incorrect password 
                else:
                    print(Fore.RED + "\nIncorrect password." + Style.RESET_ALL)
                    attempts += 1
                    time.sleep(2)
                    print(Fore.RED + f"\nRemaining attempts: {MAX_ATTEMPTS - attempts}" + Style.RESET_ALL)
                    log_action(username, "Failed attempted access via sudo")
                    time.sleep(2)
                    clear_screen()

            
        # Notify about non-existing username
        else:
            print(Fore.RED + "\nUsername not found. Please try again." + Style.RESET_ALL)
            time.sleep(2)
            clear_screen()
        
    
    print(Fore.RED + "\nMaximum login attempts reached" + Style.RESET_ALL)
    time.sleep(1)
    print("\nExiting...")
    time.sleep(2)
    exit()
           