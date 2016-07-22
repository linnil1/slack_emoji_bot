from http.server import BaseHTTPRequestHandler, HTTPServer
from slackclient import SlackClient
from CustomizeSlack import Customize
from OLD_command import OLD_command
import urllib.parse
import json

class ntuosc:
    def __init__(self):
        #from privacy
        privacy = json.loads(open("privacy.json").read())
        self.custom= Customize(privacy)
        self.slack = SlackClient(privacy['token'])
        self.old   = OLD_command(self.slack,self.custom)

    def commandSelect(self,body):
        #body to dict
        datadict = {}
        for data    in body.split("&"):
            datatwo = data.split("=") 
            datadict[datatwo[0]] = datatwo[1]
        datadict['text'] = urllib.parse.unquote(datadict['text'].replace("+"," ")).strip()
        print(datadict['text'])

        #select
        if datadict['text'].startswith(self.old.keyword):
            self.old.main(datadict)

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
        ntu.commandSelect(body)

def run(port):
    httpd = HTTPServer(('', port), Slackbot_server)
    print("start")
    httpd.serve_forever()

run(6112)
