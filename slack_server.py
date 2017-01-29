import InitModule
from slackclient import SlackClient
import ColorPrint
import copy

import sys
import time
import signal

class Slack_RTM:
    def __init__(self):
        self.modules, self.slack = InitModule.ModuleInit() 
        self.colorPrint = ColorPrint.setPrint("Root")
        self.slack = SlackClient(self.slack) #dirty methods
        signal.signal(signal.SIGTERM, self.graceExit)
        signal.signal(signal.SIGHUP,  self.graceExit)
        self.ignoretype = ['user_typing','reconnect_url','pref_change','presence_change','emoji_changed','desktop_notification']

    def startRTM(self):
        if self.slack.rtm_connect():
            self.colorPrint("Start")
            while True:
                data = self.slack.rtm_read()
                if data and data[0]['type'] not in self.ignoretype:
                    self.colorPrint("GET",data)
                if not data:
                    time.sleep(1)
                else:
                    self.commandSelect(data[0])
        else:
            self.colorPrint("Connect Error!","Please Reconnect",color="ERR")

    def start(self):
        while True:
            try:
                self.startRTM();
            except KeyboardInterrupt:
                break
            except:
                self.colorPrint("ERR",sys.exc_info(),color="ERR")
                time.sleep(1)

    def commandSelect(self,data):
        for mod in self.modules:
            try:
                mod.main(copy.deepcopy(data))
            except KeyboardInterrupt:
                raise
            except:
                self.colorPrint("ERR at ",mod,color="ERR")
                self.colorPrint("ERR",sys.exc_info(),color="ERR")
                time.sleep(1)

    def graceExit(self, signum, frame):
        rep = self.slack.api_call("channels.list")
        for c in rep['channels']:
            if c['name'].lower() == self.slack.reportchannel:
                self.slack.api_call("chat.postMessage",channel=c['id'],text="Killed at "+time.strftime("%c"))
                self.colorPrint("Killed at ",time.strftime("%c"),color="ERR")
                sys.exit()

slack_rtm=  Slack_RTM()
slack_rtm.start()
