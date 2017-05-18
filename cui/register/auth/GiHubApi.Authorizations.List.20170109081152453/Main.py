#!python3
#encoding:utf-8
import sqlite3
#from AuthList import AuthList
import AuthList
import traceback

#
# DBからアカウント情報を取得する
#
db_path = 'C:/root/db/Account/GitHub/private/GitHub.Accounts.sqlite3'
connector = sqlite3.connect(db_path)
cursor = connector.cursor()
sql = "select * from Accounts;"
cursor.execute(sql)
accounts = cursor.fetchall()
#
# アカウントごとにToken情報を取得する
#
auth = AuthList.AuthList()
for account in accounts:
    auth.get(account[1], account[2])
