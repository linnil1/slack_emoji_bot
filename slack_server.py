from slackclient import SlackClient
from CustomizeSlack import Customize
from OLD_command import OLD_command
import json

import multiprocessing as mp
import time
import sys
import queue

class ntuosc:
    def __init__(self):
        #from privacy
        privacy = json.loads(open("privacy.json").read())
        self.custom= Customize(privacy)
        self.slack = SlackClient(privacy['token'])
        self.old   = OLD_command(self.slack,self.custom)

        self.pq = queue.PriorityQueue()

    def processTimeout(self):
        while not self.pq.empty():
            t,p = self.pq.get()
            if  (not p.is_alive()) or time.time() - t > 30 : #too long
                p.terminate()
                p.join()
            else:
                self.pq.put((t,p))
                break

    def startRTM(self):
        self.pq = queue.PriorityQueue()
        if self.slack.rtm_connect():
            print("Start")
            while True:
                self.processTimeout()
                data = self.slack.rtm_read()
                if data:
                        print(data)
                        try:
                            p =  mp.Process(target=self.commandSelect,args=(data[0],))
                            p.start()
                            print(p.pid)
                            self.pq.put( (time.time(),p) )
                        except not KeyboardInterrupt:
                            print(sys.exc_info())
                else:
                    time.sleep(1)


    def commandSelect(self,data):
        if data['type'] == 'message' and (
        'subtype' not in data or data['subtype']=="bot_message"):
            self.old.main(data)


ntu =  ntuosc()
ntu.startRTM()
