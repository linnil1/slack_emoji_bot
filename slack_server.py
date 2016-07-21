from http.server import BaseHTTPRequestHandler, HTTPServer
from upload_emoji import Emoji
from slackclient import SlackClient
import urllib.parse
import json
import re

class ntuosc:
    def __init__(self):
        #from privacy
        privacy = json.loads(open("privacy.json").read())
        self.emoji = Emoji(privacy['team_name'],privacy['email'],privacy['password'])
        self.slack= SlackClient(privacy['token'])

    def bodyDict(self,body):
        self.dict = {}
        for data    in body.split("&"):
            dictdata = data.split("=") 
            self.dict[dictdata[0]] = dictdata[1]
        self.dict['text'] = urllib.parse.unquote(self.dict['text'].replace("+"," ")).strip()

    def commandSelect(self):
        print(self.dict['text'])
        payload = {
            "channel": self.dict['channel_id'],
            "text": "Error", 
            "username": "stranger",
            "icon_emoji": ":strange:"}

        command = re.search(r"\w+",self.dict['text']).group().strip()
        if command == 'old':
            payload["username"  ] = "小篆transformer"
            payload["icon_emoji"] = ":_e7_af_86:"
            if "'" in self.dict['text']:
                payload["text"  ] = self.emoji.imageUpDown(u"「請勿輸入單引號，判定為攻擊！」")
                self.slack.api_call("chat.postMessage",**payload)
                
            data = re.search(r"(?<=old ).*",self.dict['text']).group().strip()
            payload["text"      ] = self.emoji.imageUpDown(data)
            print(self.slack.api_call("chat.postMessage",**payload))

        elif command == 'askold':
            payload["username"  ] = "小篆transformer"
            payload["icon_emoji"] = ":_e7_af_86:"
            data = re.search(r"(?<=askold ).*",self.dict['text']).group().strip()
            if len(data)==6:
                udata = "%{}%{}%{}".format(data[0:2],data[2:4],data[4:6])
                data = urllib.parse.unquote(udata)
                payload["text"] = self.emoji.imageUpDown(data)+" = "+udata
                print(self.slack.api_call("chat.postMessage",**payload))

ntu =  ntuosc()

class Slackbot_server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        #self.wfile.write("<html><body><h1>hi!</h1></body></html>")
        self.wfile.write("Get".encode("utf8"))

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        #print(self.headers)
        body_len = int(self.headers['content-length'])
        body = self.rfile.read(body_len).decode("utf8")
        
        print(body)
        ntu.bodyDict(body)
        ntu.commandSelect()



def run(port):
    httpd = HTTPServer(('', port), Slackbot_server)
    print("start")
    httpd.serve_forever()

run(6112)
