from slackclient import SlackClient
from CustomizeSlack import Customize
from OLD_command import OLD_command
from KXGEN_command import KXGEN
from VOTE_command import VOTE
from Course_command import Course 
from Food_command import Midnight 
from POFB_command import POFB
import password_crypt 

import time
import sys

class ntuosc:
    def __init__(self):
        #from privacy
        privacy = password_crypt.logIn()
        self.custom= Customize(privacy)
        self.slack = SlackClient(privacy['token'])
        self.old   = OLD_command(self.slack,self.custom)
        self.kxgen = KXGEN      (self.slack,self.custom)
        self.vote  = VOTE       (self.slack,self.custom)
        self.course= Course     (self.slack,self.custom)
        self.food  = Midnight   (self.slack,self.custom)
        self.pofb  = POFB       (self.slack,self.custom)

    def startRTM(self):
        if self.slack.rtm_connect():
            print("Start")
            while True:
                data = self.slack.rtm_read()
                if data and data[0]['type'] not in ['user_typing','reconnect_url','pref_change','presence_change','emoji_changed']:
                    print(data)
                try:
                    self.commandSelect(data[0] if data else {"type":None})
                    if not data:
                        time.sleep(1)
                except KeyboardInterrupt:
                    raise
                except:
                    print(sys.exc_info())
                    time.sleep(1)
        else:
            print("Connect Error! Please Reconnect")

    def start(self):
        while True:
            try:
                self.startRTM();
            except KeyboardInterrupt:
                break
            except:
                print(sys.exc_info())
                time.sleep(1)


    def commandSelect(self,data):
        self.old   .main(data)
        self.kxgen .main(data)
        self.vote  .main(data)
        self.course.main(data)
        self.food  .main(data)
        self.pofb  .main(data)


ntu =  ntuosc()
ntu.start()
