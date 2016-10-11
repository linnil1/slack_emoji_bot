import re
import urllib
class POFB:
    def __init__(self,slack,custom):
        self.slack = slack
        self.custom = custom
        self.poFBurl = "http://home.ntuosc.org/~linnil1/poFB.html"

    def main(self,datadict):
        if datadict['type'] == 'message' and datadict['text'].startswith("pofb "):
            text = re.search(r"(?<=pofb ).*",datadict['text'],re.DOTALL).group().strip()

            self.slack.api_call("chat.postMessage",**{
                "text": "<"+self.poFBurl+"?"+urllib.parse.quote(text)+"|Post it by this link>",
                "username": "FBposter",
                "icon_emoji": "_e8_bd_89",
                "channel": datadict['channel']})

