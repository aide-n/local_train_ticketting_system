import sqlite3
import qrcode
import bcrypt
from stdiomask import getpass  # external library to get password safely by masking password entered onscreen
from prettytable import from_db_cursor as db

# Connect to the SQLite database (or create a new one if it doesn't exist)
conn = sqlite3.connect("ticketing.db")  # connection to database
cursor = conn.cursor()  # cursor


class Booking_system:

    def __init__(self):
        print("""
========================================================================================================
                        WELCOME TO OUR LOCAL TRAIN TICKETING SYSTEM
========================================================================================================""")

    # view available trains:
    def view_trains(self):
        cursor.execute("SELECT id, number, name, source, destination, arrival, departure, price FROM trains")
        train_table = db(cursor)
        print(train_table)

    def arrange_table(self,updated_row):
        cursor.execute('''UPDATE trains SET id = id - 1 WHERE id >?''', (updated_row,))
        conn.commit()

    # QR generator
    def generate_payment_qr(self, amount, description):

        ###url= "https://payment portal website hyperlink"###-- payment portal hyper link can be inserted in further updates
        payment_info = f"Payment for {description}\nAmount: ₹{amount}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(payment_info)
        qr.make(fit=True)

        # Create an image from the QR Code instance
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img.save("img.png")
        # Display or save the QR code image (you can customize this part)
        qr_img.show()

    # PASSWORD HASHING
    def hash_password(self, password):
        salt = b'$2b$12$eIprcLVK/7iq7shkCP1cse' #salt seed better concealed in db itself
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        print(hashed_password)
        return hashed_password

    # check password
    def check_password(self, username, pswd_chk):
        # Fetch hashed password from the database based on the entered username
        cursor.execute('SELECT hashed_password FROM admins WHERE username =?', (username,))
        result = cursor.fetchone()

        if result:
            stored_password = result[0]
            return bcrypt.checkpw(pswd_chk.encode('utf-8'), stored_password)
        else:
            return False

    # admin authentication
    def auth_admin(self):
        username = input("Admin     ::")
        pswd_chk = input("password  ::")
        if self.check_password(username, pswd_chk):
            print("Admin authentication succesfull")
            return True
        else:
            print("Admin authentication failed")

#+++++++++++++++++++++++++++++++++++++++++TRAIN UPDATE FUNCTIONS++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # add train
    def add_train(self):
        no = input("Number of the train         : ")
        trn_name = input("Name of the train         : ")
        cursor.execute('SELECT 1 FROM trains WHERE number =? AND name=? LIMIT 1', (no, trn_name,))
        check = cursor.fetchone()
        if check:
            print("|--This Train already exist--|")
        else:
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
                        VALUES(?,?,?,?,?,?,?)''', (no, trn_name, dest, src, arvl, dept, prc,))

            conn.commit()
        print(f"New Train [{no}]{trn_name} Succesfully added \n ------------Reverting to main menu------------")


    # edit train data
    def edit_train(self):
        self.view_trains()
        train_2edit = input("Give the Train index you wish to edit \n:")
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
        cursor.execute('SELECT * FROM trains WHERE id=?', (train_2edit,))
        pr = cursor.fetchone()
        print(pr[1])
        cursor.execute('''UPDATE trains  
        SET number =?, name =?, destination =?, source =?, arrival =?, departure =?, price =? WHERE id=?''',
                       (no, trn_name, dest, src, arvl, dept, prc, train_2edit,))
        conn.commit()
        self.arrange_table(train_2edit)
        print(f""" Train [{pr[1]}]{pr[2]} is updated Suceesully
\n ------------Reverting to main menu------------""")

    # edit train
    def delete_train(self):
        global train_2delete
        self.view_trains()
        while True:
            try:
                train_2delete = int(input("Give Index of  train to delete \n:"))
            except(ValueError, IndexError):
                print("give valid index")

            cursor.execute('''SELECT * FROM trains WHERE id=?''', (train_2delete,))
            del_train = cursor.fetchone()
            d = del_train[2]
            cursor.execute('''DELETE FROM trains WHERE id=?''', (train_2delete,))
            conn.commit()
            self.arrange_table(train_2delete)
            print(f"Train {d} is deleted succesfully")
            break


# +++++++++++++++++++++++++++++++++++++++++++TRAIN UPDATE MENU+++++++++++++++++++++++++++++++++++++++++++++++
    def trains_menu(self):

        print("""
                            |=============Train update menu===========|
                            |               1.Add train               |
                            |       2.Update Existing train data      |
                            |          3.Delete existing Train        |
                             -------------------------------------------""")

        opts = input("Option to proceed with\n:")
        if opts == "1":
            self.add_train() #line 81
        # -------->add train function
        elif opts == "2":
            self.edit_train()
        # -------->update existing train function
        elif opts == "3":
            self.delete_train()

    # --------> delete trains function

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ++++++++++++++++++++++++++++++++++++++++++++ADMIN UPDATE FUNCTIONS+++++++++++++++++++++++++++++++++++++++++++++++++
    # update admin functions
    # add admins
    def add_admin(self):
        while True:
            new_admin = input("New admin username       : ")
            new_password = getpass("Password              : ", mask='*')
            check = cursor.execute('SELECT username FROM admins WHERE username =?', (new_admin,))
            if check:
                hash_pswd = self.hash_password(new_password)
                cursor.execute('''
                             INSERT INTO admins (username, hashed_password)
                             VALUES (?,?)''', (new_admin, hash_pswd))

                conn.commit()
                print(f"------New admin id {new_admin} is added succesfully-------")
            else:
                print("\n|--Admin user id already exist--|")

    # edit admin
    def edit_admin(self):
        while True:
            admin_2edit = input("Admin username to edit \n:")
            check = cursor.execute('SELECT username FROM admins WHERE username =?', (admin_2edit))

            if check:
                new_admin = input("New admin            :")
                new_password = getpass("New password         :", mask='*')
                new_haspw = self.hash_password(new_password)
                cursor.execute('''
                UPDATE admins WHERE username =? 
                SET username =?, password =? ''', (admin_2edit, new_admin, new_haspw,))

                conn.commit()
                print(f" Existing {admin_2edit} is Succesfully changed to {new_admin} ")
                break
            else:
                print("|--Give valid admin username--|")

    # delete admin
    def delete_admin(self):

        for i in range(3):
            delete_user = input("Admin id to delete\n:")
            check = input("confirm delete (YES/NO)").upper()
            if check:
                cursor.execute('DELETE FROM admins WHERE username=?', (delete_user,))
            if i == 3:
                print("Reverting to main menu")
                break
            else:
                print("|--Give valid option--|")

#-----------------------------------------Admin update menu-------------------------
    def admin_update(self):
        print("""
                            |=============Admin update menu===========|
                            |               1.Add New admin           |
                            |           2.Update Existing Admin       |
                            |           3.Delete existing admin       |
                            -------------------------------------------\n""")
        for i in range(3):
            opts = print("Give option to proceed with \n:")

            if opts == "1":
                self.add_admin()

            elif opts == "2":
                self.edit_admin()

            elif opts == "3":
                self.delete_admin()
            else:
                print("Try again")
            if i == 3:
                print("reverting to main menu")
            break

# ++++++++++++++++++++++++++++++++++++++++++++ADMIN PANEL+++++++++++++++++++++++++++++++++++++++++++++
    # admin panel
    def admin_opts(self):
        if self.auth_admin():  # line 70
            # admin menu

            opts = input("""
                            |=============Admin menu=============|
                            |        1.Update Train data         |
                            |        2.Update admin data         |
                            --------------------------------------\n\ngive your option to proceed:""")
            #update train data
            if opts == "1":
                self.trains_menu()  #line 142
            # update admin data
            elif opts == "2":
                self.admin_update() #line 219

#+++++++++++++++++++++++++++++++++++++++TICKET BOOKING / PURCHASE++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def booking(self):
        self.view_trains()
        while True:
                try:
                    train = int(input("Train index you wish to book : "))
                    break
                except (ValueError, TypeError):
                    print("|--Give valid train index--|")

        cursor.execute('SELECT * FROM trains WHERE id=?', (train,))
        t_b = cursor.fetchone()
        b="not break"
        while b != "break":
            opt = input(f""" Choosen train [{t_b[1]}] {t_b[2]} from {t_b[3]} to {t_b[4]} 
                 do you wish to continue (Y/N) : """).upper()
            if opt == "Y":
                while True:
                    try:
                        tickets = int(input(" How many tickets you wish to buy : "))
                    except:
                        print("Give the correct train index")

                    amount = tickets * t_b[7]
                    print(f" Total cost of {tickets} tickets is {amount}")
                    description = f"payment for {tickets} is {amount}"
                    self.generate_payment_qr(amount, description)
                    print("\nScan QR for payment")
                    b = "break"
                    break

            elif opt == "N":
                opts = input("do you want to book different train (y/n) \n: ").lower()

                if opts == "y":
                    print("reverting to train selection")
                    break
                else:
                    b = "break"
                    print("reverting to main menu")

            else:
                print("give valid value")

# --------------------------------------MAIN MENU-------------------------------------
    def main_menu(self):

        while True:
            print("""
                            |==========main menu=============|
                            |        1.Admin Login           |
                            |    2.show available Trains     |
                            |        3.Book a ticket         |
                            ----------------------------------\n""")

            option = input("give your choice :")
            if option == "1":
                self.admin_opts() #line 238
            # ------>admins option function
            elif option == "2":
                self.view_trains()# line 17
            # ------->view trains function
            elif option == "3":
                self.booking() #line 259
            # --------> booking function


# ----------------------------------------------------------------------------


def main():
    book = Booking_system()

    book.main_menu()


if __name__ == "__main__":
    main()