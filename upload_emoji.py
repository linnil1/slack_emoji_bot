import os
import requests
from bs4 import BeautifulSoup

class Emoji:
    def __init__(self,team_name,email,password):
        self.baseurl = "https://{}.slack.com".format(team_name)
        self.url = self.baseurl+"/customize/emoji"
        self.se = requests.Session()

        #login
        self.rep = self.se.get(self.url, allow_redirects=True)
        self.rep.raise_for_status()

        #login
        soup = BeautifulSoup(self.rep.text)
        print(soup.find("h1").text.strip())
        crumb = soup.find("input", attrs={"name": "crumb"})["value"]
        data = {
            'crumb': crumb,
            'email': email,
            'password': password,
            'redir': "/customize/emoji",
            'remember': "on",
            'signin': 1
        }
        self.rep = self.se.post(self.baseurl,data=data, allow_redirects=True)
        self.rep.raise_for_status()

        soup = BeautifulSoup(self.rep.text).find_all("h1")
        print("team_name = "+soup[0].text.strip())
        print(soup[1].text.strip())

    def imageUpload(self,filename):
        soup = BeautifulSoup(self.rep.text)
        crumb = soup.find("input", attrs={"name": "crumb"})["value"]

        data = {
            'add': 1,
            'crumb': crumb,
            'name': filename,
            'mode': 'data',
        }
        files = {'img': open("word_data/"+filename, 'rb')}
        self.rep = self.se.post(self.url, data=data, files=files, allow_redirects=True)
        self.rep.raise_for_status()
        print(BeautifulSoup(self.rep.text).find("p","alert").text.strip())
