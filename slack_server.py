import InitModule
from slackclient import SlackClient
import copy

import sys
import time

class Slack_RTM:
    def __init__(self):
        self.modules,self.slack = InitModule.ModuleInit() 
        self.slack = SlackClient(self.slack) #dirty methods

    def startRTM(self):
        if self.slack.rtm_connect():
            print("Start")
            while True:
                data = self.slack.rtm_read()
                if data and data[0]['type'] not in ['user_typing','reconnect_url','pref_change','presence_change','emoji_changed']:
                    print(data)
                try:
                    if not data:
                        time.sleep(1)
                    else:
                        commandSelect(data[0])
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
        for mod in self.modules:
            mod.main(copy.deepcopy(data))

slack_rtm=  Slack_RTM()
slack_rtm.start()
