#!python3
#encoding:utf-8
import sqlite3
#from AuthList import AuthList
import AuthList
import traceback
import pyotp
import dataset

username = 'csharpstudy0'
password = 'takasa02080'
two_factor_secret = 'dubueq7po5mb4wjf'
auth = AuthList.AuthList()
totp = pyotp.TOTP(two_factor_secret)
otp = totp.now()
auth.get(username, password, otp)
print("otp = {0}".format(otp))

"""
db_connect_str = 'sqlite:///C:/root/db/Account/GitHub/private/GitHub.Accounts.sqlite3'
db = dataset.connect(db_connect_str)
auth = AuthList.AuthList()
for two_factor in db['TwoFactors']:
    print(two_factor)
for account in db['Accounts']:
#    two_factor = db['TwoFactors'].find(AccountId = account["Id"])
    two_factor = db['TwoFactors'].find_one(AccountId = account["Id"])
    print(two_factor)
#    auth.get(account['Username'], account['Password'])
#    print(account)
#    print("id:{0},user:{1},pass:{2},mail:{3},create:{4}".format(account["Id"],account["Username"],account["Password"],account["MailAddress"],account["CreatedAt"]))
"""

#for account in accounts:
#    auth.get(account[1], account[2])

#
# DBからアカウント情報を取得する
#
#def get_accounts():
#    db_path = 'C:/root/db/Account/GitHub/private/GitHub.Accounts.sqlite3'
#    connector = sqlite3.connect(db_path)
#    cursor = connector.cursor()
#    sql = "select * from Accounts;"
#    cursor.execute(sql)
#    return cursor.fetchall()
#
# アカウントごとにToken情報を取得する
#
#auth = AuthList.AuthList()
#for account in accounts:
#    auth.get(account[1], account[2])

#
# 二要素認証
#
#def get_two_factor_secret(account_id):
#    

#totp = pyotp.TOTP('base32secret3232')
#totp.now() # => 492039

