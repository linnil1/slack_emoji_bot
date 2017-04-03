from slackclient import SlackClient
import copy
import sys
import time
import os
import re
import importlib
import InitModule
import ColorPrint
import password_crypt
sys.path.insert(0, './modules/')
sys.path.insert(0, './common/')

# wantname = ["REGEXBOT","CustomResponse"]
wantname = ["FBTOSLACK"]


class Slack_RTM:
    def __init__(self):
        self.colorPrint = ColorPrint.setPrint("Root")
        self.colorPrint("Test Unit", wantname)

        modules = InitModule.requiresCall()
        privacy = password_crypt.logIn(InitModule.requiresGet(modules))
        # self.colorPrint("Secret",privacy,color="WARNING")
        modules = [i for i in modules if i['name'] in ["", *wantname]]

        self.modules, base = InitModule.initSet(privacy, modules)
        self.slack = SlackClient(base.get('TOKEN'))
        self.ignoretype = [
            'user_typing',
            'reconnect_url',
            'pref_change',
            'presence_change',
            'emoji_changed',
            'desktop_notification']

    def startRTM(self):
        if self.slack.rtm_connect():
            self.colorPrint("Start")
            while True:
                data = self.slack.rtm_read()
                if data and data[0]['type'] not in self.ignoretype:
                    self.colorPrint("GET", data)

                if not data:
                    time.sleep(1)
                else:
                    self.commandSelect(data[0])
        else:
            self.colorPrint("Connect Error!", "Please Reconnect", color="ERR")

    def start(self):
        self.startRTM()

    def commandSelect(self, data):
        for mod in self.modules:
            mod.main(copy.deepcopy(data))


if __name__ == "__main__":
    slack_rtm = Slack_RTM()
    slack_rtm.start()
