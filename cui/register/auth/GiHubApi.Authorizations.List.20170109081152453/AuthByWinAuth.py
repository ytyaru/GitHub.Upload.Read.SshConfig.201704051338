#!python3
#encoding:utf-8
from tkinter import Tk
#from Tkinter import Tk => python2
import AuthList

username = 'csharpstudy0'
password = 'takasa02080'
auth = AuthList.AuthList()
otp = Tk().clipboard_get()
auth.get(username, password, otp)
print("otp = {0}".format(otp))
