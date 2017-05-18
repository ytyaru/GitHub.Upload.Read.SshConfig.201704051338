#!python3
#encoding:utf-8
import sqlite3
#from AuthList import AuthList
import AuthList
import traceback
import pyotp

class AccountGetter:
    def __init__(self):

    def connect(self, db_path):
        self.connector = sqlite3.connect(db_path)
        self.cursor = connector.cursor()

