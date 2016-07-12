import os
import requests
from bs4 import BeautifulSoup

class Emoji:
    def __init__(self,team_name,email,password):
        self.baseurl = "https://{}.slack.com".format(team_name)
        self.url = self.baseurl+"/customize/emoji"
        self.se = requests.Session()

        #login
        r = self.se.get(self.url, allow_redirects=True)
        r.raise_for_status()

        #login
        soup = BeautifulSoup(r.text)
        print(soup.find("h1"))
        crumb = soup.find("input", attrs={"name": "crumb"})["value"]
        data = {
            'crumb': crumb,
            'email': email,
            'password': password,
            'redir': "/customize/emoji",
            'remember': "on",
            'signin': 1
        }
        r = self.se.post(self.baseurl,data=data, allow_redirects=True)
        r.raise_for_status()
        print(BeautifulSoup(r.text).find_all("h1"))

    def imageUpload(self,filename,emoji_name):
        r = self.se.get(self.url, allow_redirects=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.text)
        crumb = soup.find("input", attrs={"name": "crumb"})["value"]

        data = {
            'add': 1,
            'crumb': crumb,
            'name': emoji_name,
            'mode': 'data',
        }
        files = {'img': open(filename, 'rb')}
        r = self.se.post(self.url, data=data, files=files, allow_redirects=True)
        r.raise_for_status()
        print(BeautifulSoup(r.text).find_all("p","alert"))
