#!python3
#encoding:utf-8
import requests

class AuthList:
    def __init__(self):
        pass

    def get(self, username, password):
        url = 'https://api.github.com/authorizations'
        headers = {'Time-Zone': 'Asia/Tokyo'}
        r = requests.get(url, headers=headers, auth=(username, password))
        with open('GiHubApi.Authorizations.List.{0}.json'.format(username), 'w') as f:
            f.write(r.text)
            print(r.text)

    def get(self, username, password, otp):
        url = 'https://api.github.com/authorizations'
        headers = {'Time-Zone': 'Asia/Tokyo', 'X-GitHub-OTP': otp}
        print(headers)
        r = requests.get(url, headers=headers, auth=(username, password))
        with open('GiHubApi.Authorizations.List.{0}.json'.format(username), 'w') as f:
            f.write(r.text)
            print(r.text)
