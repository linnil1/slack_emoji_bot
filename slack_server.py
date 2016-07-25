from slackclient import SlackClient
from CustomizeSlack import Customize
from OLD_command import OLD_command
import json

import multiprocessing as mp
import time

class ntuosc:
    def __init__(self):
        #from privacy
        privacy = json.loads(open("privacy.json").read())
        self.custom= Customize(privacy)
        self.slack = SlackClient(privacy['token'])
        self.old   = OLD_command(self.slack,self.custom)

    def startRTM(self):
        if self.slack.rtm_connect():
            print("Start")
            while True:
                data = self.slack.rtm_read()
                if data:
                        print(data)
                        try:
                            self.commandSelect(data[0])
                        except not KeyboardInterrupt:
                            print(sys.exc_info())
                else:
                    time.sleep(1)


    def commandSelect(self,data):
        self.old.main(data)


ntu =  ntuosc()
ntu.startRTM()
