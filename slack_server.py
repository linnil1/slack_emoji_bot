from http.server import BaseHTTPRequestHandler, HTTPServer
from upload_emoji import Emoji
import urllib.parse
import re

emoji = Emoji()

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
        body = urllib.parse.unquote(body)
        print(body)

        command = re.search(r"(?<=text=)\w+",body).group().strip()
        channel = re.search(r"(?<=channel_id=)\w+",body).group()

        print(command)
        if command == "old":
            data = re.search(r"(?<=text=old\+).*?(?=&)",body).group().strip()
            emoji.imageUpDown(data,channel)
            print(" -> "+data)

        elif command == "askold":
            data = re.search(r"(?<=text=askold\+)\w+",body).group().strip()
            if len(data)==6:
                udata = "%{}%{}%{}".format(data[0:2],data[2:4],data[4:6])
                udata = urllib.parse.unquote(udata)
                emoji.slackMessage(udata,channel)
            print(" -> "+data)
        
        #self.wfile.write(data.encode("utf-8"))

def run(port):
    httpd = HTTPServer(('', port), Slackbot_server)
    print("start")
    httpd.serve_forever()

run(6112)
