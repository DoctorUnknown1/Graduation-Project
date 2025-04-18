import sqlite3
import os
import pandas as pd
from utils import *
from datetime import datetime
class DBManager:
    def __init__(self, dbname="system/Database.db"):
        if not os.path.exists("system/"):
            os.mkdir("system/")
        self.dbname = dbname
        if not os.path.exists(self.dbname):
            self.con = sqlite3.connect(self.dbname)
            self.cursor = self.con.cursor()
            self.create_table_admin()
            self.create_table_criminal()
            self.close_connection()
            self.insert_into_admin()
    def close_connection(self):
        try:
            self.con.close()
        except:
            pass
    def create_table_admin(self):
        command = '''CREATE TABLE Admin(ID INTEGER PRIMARY KEY ,Username TEXT, Password TEXT,Auth TEXT)'''
        try:
            self.cursor.execute(command)
            self.con.commit()
        except Exception as e:
            print(e)
    def insert_into_admin(self, username='ali', password="1234"):
        self.con = sqlite3.connect(self.dbname)
        cursor = self.con.cursor()
        command = "SELECT * FROM Admin WHERE (Username) = ? "
        cursor.execute(command, (username,))
        rows = cursor.fetchall()
        if rows:
            pass
        else:
            command_insertvalue = "insert into Admin (Username,Password,Auth) values (?, ?,?)"
            try:
                cursor.execute(command_insertvalue, (username,password,'false'))
                self.con.commit()
                self.close_connection()
            except Exception as e:
                print(e)
    def authenticate(self,username,password):
        self.con = sqlite3.connect(self.dbname)
        cursor = self.con.cursor()
        command = "SELECT * FROM Admin WHERE (Username) = ? "
        cursor.execute(command, (username,))
        rows = cursor.fetchall()
        if rows:
            row=rows[0]
            passw=row[2]
            auth=row[3]
            if passw==password:
                return "success",auth
            else:
                return "wrong password" ,'none'
        else:
            return "failed",'none'
    def changepass(self,email,password,newpassword):
        self.con = sqlite3.connect(self.dbname)
        cursor = self.con.cursor()
        command = "SELECT * FROM Admin WHERE (Username) = ? "
        cursor.execute(command, (email,))
        rows = cursor.fetchall()
        if rows:
            row=rows[0]
            passw=row[2]
            if passw==password:
                command_update="""UPDATE Admin SET Password=? WHERE Username=? """
                try:
                    cursor.execute(command_update,(newpassword,email))
                    self.con.commit()
                    self.close_connection()
                    return "Success! User and Password Changed"
                except:
                    return "Error! Error Occured"
            else:
                return "Wrong Password"

        else:
            return "Wrong username"
    def setauth(self,email,value):
        self.con = sqlite3.connect(self.dbname)
        cursor = self.con.cursor()
        command_update="""UPDATE Admin SET Auth=? WHERE Username=? """
        try:
            cursor.execute(command_update,(value,email))
            self.con.commit()
            self.close_connection()
            return "Success! "
        except:
            return "Error Occured"
    def create_table_criminal(self):
        command = '''CREATE TABLE Criminal(ID INTEGER PRIMARY KEY , CaseId TEXT, UserName TEXT,Crime TEXT,Adress TEXT,DistMark TEXT)'''
        try:
            self.cursor.execute(command)
            self.con.commit()
        except Exception as e:
            print(e)
    def insert_into_criminal(self, id_, name,crime,adress,distmark):
        self.con = sqlite3.connect(self.dbname)
        cursor = self.con.cursor()
        command = "SELECT * FROM Criminal WHERE (CaseId) = ? "
        cursor.execute(command, (id_,))
        rows = cursor.fetchall()
        if rows:
            return "Case id already exist"
        command_insertvalue = "insert into Criminal (CaseId,UserName,Crime,Adress,DistMark) values (?, ?,?,?,?)"
        try:
            cursor.execute(command_insertvalue, (id_,name,crime,adress,distmark))
            self.con.commit()
            self.close_connection()
            return "New criminal Added"
        except Exception as e:
            print(e)
    def get_details(self,id_):
        self.con = sqlite3.connect(self.dbname)
        cursor = self.con.cursor()
        command = "SELECT * FROM Criminal WHERE (CaseID) = ? "
        cursor.execute(command, (id_,))
        rows = cursor.fetchall()
        if rows:
            row=rows[0]
            name=row[2]
            crime=row[3]
            adress=row[4]
            distmark=row[5]
            return name,crime,adress,distmark
        else:
            return None, None, None, None
    def delete_data_of_id_criminal(self, id_):
        self.con = sqlite3.connect(self.dbname)
        cursor = self.con.cursor()
        command = "DELETE FROM Criminal WHERE (CaseId) = ? "
        try:
            cursor.execute(command, (id_,))
            self.con.commit()
            self.con.close()
            return True
        except:
            return False
    def get_name_from_id(self, id_):
        self.con=sqlite3.connect(self.dbname)
        cursor = self.con.cursor()
        command = "SELECT * FROM Criminal WHERE (CaseId) = ? "
        cursor.execute(command, (id_,))
        rows = cursor.fetchall()
        if rows:
            row = rows[0]
            name = row[2]
            return name
        return None



if __name__ == "__main__":
    dbmanager = DBManager()
    
    
    