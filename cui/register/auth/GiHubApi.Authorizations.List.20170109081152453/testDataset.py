#!python3
#encoding:utf-8
import dataset

db_connect_str = 'mysql://root@127.0.0.1/information_schema'
db_connect_str = 'sqlite:///C:/root/db/Account/GitHub/private/GitHub.Accounts.sqlite3'
db = dataset.connect(db_connect_str)

for account in db['Accounts']:
    print(account)
    print("id:{0},user:{1},pass:{2},mail:{3},create:{4}".format(account["Id"],account["Username"],account["Password"],account["MailAddress"],account["CreatedAt"]))
