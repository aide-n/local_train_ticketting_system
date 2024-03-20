
import sqlite3
import bcrypt
from prettytable import from_db_cursor as db

conn = sqlite3.connect("ticketing.db")  # connection to database
cursor = conn.cursor()  # cursor
# Execute an SQL query to create a table (if not already exists)
cursor.execute('''
 CREATE TABLE IF NOT EXISTS trains (
     id INTEGER PRIMARY KEY,
     number TEXT NOT NULL,
     name TEXT NOT NULL,
     source TEXT NOT NULL,
     destination TEXT NOT NULL,
     arrival TEXT NOT NULL,
     departure TEXT NOT NULL,
     price REAL NOT NULL
     )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
         id INTEGER PRIMARY KEY,
         username TEXT NOT NULL,
         hashed_password TEXT NOT NULL   
        )
''')

class do_thing:

    def __init__(self):

        print("")


    def hash_password(self, password):

        salt = b'$2b$12$eIprcLVK/7iq7shkCP1cse' # salt to hash
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        print(hashed_password)
        return hashed_password

    def train_populate(self):

        no = input("Number of the train         : ")
        trn_name = input("Name of the train         : ")
        dest = input("Destination  station      : ")
        src = input("Source station             : ")
        arvl = input("Arrival time              : ")
        dept = input("Departure time            : ")
        while True:
            try:
                prc = float(input("Price of one ticket        : "))
                break
            except(ValueError, TypeError):
                print("|--valid price--|")

        cursor.execute('''INSERT INTO trains(
                number, name, destination, source, arrival, departure, price)
                VALUES(?,?,?,?,?,?,?)''', (no, trn_name, dest, src, arvl, dept, prc))

        conn.commit()
    def arrange_table(self,updated_row):
        cursor.execute('''UPDATE trains SET id = id - 1 WHERE id >?''', (updated_row,))
        conn.commit()


    def admin_populate(self):

        user = input("Admin username        ::") #initial will be Station master
        password = input("PASSWORD              ::")# ST password
        pswd = self.hash_password(password)
        cursor.execute('INSERT INTO admins  (username, hashed_password) VALUES(?,?)', (user, pswd,))
        conn.commit()

    def view_admins(self):  # opt 4
        cursor.execute('SELECT id, username, hashed_password FROM admins')
        admin_table = db(cursor)
        print(admin_table)

    def view_trains(self):
        cursor.execute("SELECT id, number, name, source, destination, arrival, departure, price FROM trains")
        train_table = db(cursor)
        if train_table:
            print(train_table)
        else:
            print("table is empty")

    def dissolve_table(self):
        dissolve = input("Confirm dissolving train shedule(Y/N):").upper()
        if dissolve == "Y":
            cursor.execute('DROP TABLE trains')
        else:
            print("Train schedule not deleted")


def main():
    popu = do_thing()
    while True:
            opt = input("\n 1. Train populate \n 2. admin populate \n 3. view trains \n 4. view admins "
                        "\n 5. dissolve train schedule \n 6.arrange table"
                        "\n\n'Break' to end program"
                        ":: ").lower()
            if opt == "1":
                    popu.train_populate()
            if opt =="2":
                    popu.admin_populate()
            if opt == "3":
                    popu.view_trains()
            if opt == "4":
                    popu.view_admins()
            if opt =="5":
                    popu.dissolve_table()
            if opt == "6":
                    popu.arrange_table(3)
            if opt == "break":
                break
            else:
                print("reverting")

if __name__ == "__main__":
    main()

"""
DEMO admin for testing 
Admin username        ::11
PASSWORD              ::11
----------------------------------------------------------------------------------
Admin username        ::Station master
PASSWORD              ::ST password
hashed_pw = b'$2b$12$eIprcLVK/7iq7shkCP1cseX7hAKReYk22h6VmLtj68uG2mfkl9PvW'

"""
