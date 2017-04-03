import InitModule
from slackclient import SlackClient
import ColorPrint
import copy

import sys
import time
import signal
import os

class Slack_RTM:
    def __init__(self):
        signal.signal(signal.SIGTERM, self.graceExit)
        signal.signal(signal.SIGHUP,  self.graceExit)
        self.colorPrint = ColorPrint.setPrint("Root")

        self.modules, base = InitModule.modulesInit() 
        self.slack = SlackClient(base.get("TOKEN")) #dirty methods
        self.postchannel = base.get("postchannel") #dirty methods
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
                    self.colorPrint("GET",data)
                if not data:
                    time.sleep(1)
                else:
                    self.commandSelect(data[0])
        else:
            self.colorPrint("Connect Error!","Please Reconnect",color="ERR")
            time.sleep(1)

    def start(self):
        while True:
            try:
                self.startRTM();
            except (KeyboardInterrupt, SystemExit):
                break
            except:
                self.colorPrint("ERR",sys.exc_info(),color="ERR")
                time.sleep(1)
        self.colorPrint("END")
        # I don't know why it cannot exit
        os.kill(os.getpid(), signal.SIGKILL)

    def commandSelect(self,data):
        for mod in self.modules:
            try:
                mod.main(copy.deepcopy(data))
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.colorPrint("ERR at ",mod,color="ERR")
                self.colorPrint("ERR",sys.exc_info(),color="ERR")
                time.sleep(1)

    def graceExit(self, signum, frame):
        string = "Killed at {} with signal {}".format(time.strftime("%c"),signum)
        self.colorPrint("Kill",string,color="ERR")
        self.slack.api_call("chat.postMessage",
                channel='#'+self.postchannel,
                text=string)
        sys.exit()

if __name__ == "__main__":
    slack_rtm = Slack_RTM()
    slack_rtm.start()
