import requests
import base64
import re

class KXGEN:
    def __init__(self,slack,custom):
        self.app = {
                "jiade":"假的！產生器",
                "wada" :"和田教授產生器",
                "interrupt":"抱歉打斷您產生器"}
        self.keyword = "kxgen"
        self.slack = slack
        self.custom= custom

    def pngDownload(self,name,pagename,param={}):
        data = {
                "app_param_app_name":name,
                "app_param_app_page_name":pagename,
                **param}

        url = "https://api.kxg.io/api/v1/"+name+"_img/preview" 
        header = {
            "Referer": "https://app.kxg.io/"+name+"/"
        }

        se = requests.Session()
        se.headers.update(header)
        img = se.post(url,data=data)
        # if a is ok
        img = re.search(r"(?<=,).*",img.json()['image']).group()
        img = base64.decodestring(img.encode("utf-8"))
        return img

    def paramParse(self,text):
        retext = re.findall(r'(?:(\w+)(?: *= *))?("(?:[^"\\]|\\.)*")',text)
        print(retext)
        
        checkstr = ""
        for i in retext:
            checkstr += i[0]
            if i[0]:
                checkstr += "="
            checkstr += "".join(i[1].split())
        
        if "".join(text.split()) != checkstr:
            raise ValueError("parse Error")

        relist = {}
        num = 1
        for i in retext:
            param_key = "app_param_"+i[0]
            if not i[0]:
                param_key = "app_param_text"+str(num)
                num += 1
            relist[param_key] = i[1][1:-1]

        return relist
    
    def messageSend(self,channel,text):
        print(
        self.slack.api_call("chat.postMessage",
                channel  = channel,
                username = "KXGEN_BOT",
                icon_url = "https://app.kxg.io/images/logo.png",
                text     =  text)
        )
    def getHelp(self,channel,function="",errorword=""):
        if not function:
            helptext = "Grab the strange PNGimage from https://app.kxg.io\n"
            helptext+= "Usage: kxgen [function [functionname]] [params...]\n"
            helptext+= "Type kxgen [function] to get params details\n"
            self.messageSend(channel,helptext)
        self.messageSend(channel,errorword)

    def main(self,datadict):
        if not datadict['type'] == 'message':
            return 

        payload = {
                'channels':datadict['channel'],
                'filename':datadict['ts']}
        text = datadict['text']

        if text.startswith("kxgen "):
            data = re.search(r"(?<=kxgen ).*",text,re.DOTALL).group().strip()
            
            datasplit = data.split()
            app = datasplit[0]

            try:
                if app in self.app:
                    appname = self.app[app]
                    if len(datasplit)>1 and datasplit[1] == appname:
                        data = re.findall(r"^(?:"+app+" *"+appname+" *)(.*)",data,re.DOTALL)[0]
                    else:
                        data = re.findall(r"^(?:"+app+" *)(.*)",data,re.DOTALL)[0]
                else:
                    appname = datasplit[1]
                    data = re.findall(r"^(?:"+app+" *"+appname+" *)(.*)",data,re.DOTALL)[0]
            except IndexError:
                self.getHelp(app,"params error")
                return 

            param = self.paramParse(data)
            payload['files'] = {'file':self.pngDownload( app, appname, param)}
            print(self.slack.api_call("files.upload",**payload))

        elif text.startswith("kxgenhelp"):
            channel = datadict['channel']
            if text == kxgenhelp:
                self.getHelp(channel)
            
