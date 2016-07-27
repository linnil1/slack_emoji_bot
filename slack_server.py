from slackclient import SlackClient
from CustomizeSlack import Customize
from OLD_command import OLD_command
from KXGEN_command import KXGEN
import json

import multiprocessing as mp
import time
import sys

class ntuosc:
    def __init__(self):
        #from privacy
        privacy = json.loads(open("privacy.json").read())
        self.custom= ""#Customize(privacy)
        self.slack = SlackClient(privacy['token'])
        self.old   = OLD_command(self.slack,self.custom)
        self.kxgen = KXGEN(self.slack,self.custom)

    def startRTM(self):
        if self.slack.rtm_connect():
            print("Start")
            while True:
                data = self.slack.rtm_read()
                if data:
                    if data[0]['type'] in ['user_typing','reconnect_url','pref_change']:
                        continue
                    print(data)
                    try:
                        self.commandSelect(data[0])
                    except KeyboardInterrupt:
                        break;
                    except:
                        print(sys.exc_info())
                else:
                    time.sleep(1)
        else:
            print("Connect Error! Please Reconnect")


    def commandSelect(self,data):
        self.old.main(data)
        self.kxgen.main(data)


ntu =  ntuosc()
ntu.startRTM()
