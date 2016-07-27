import requests
import base64
import re
from bs4 import BeautifulSoup as BS

class KXGEN:
    def __init__(self,slack,custom):
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

    def paramParse(self,text,params):
        retext = re.findall(r'(?:(\w+)(?: *= *))?("(?:[^"\\]|\\.)*")',text)
        print(params)
        print(retext)
        
        checkstr = ""
        for i in retext:
            checkstr += i[0]
            if i[0]:
                checkstr += "="
            checkstr += "".join(i[1].split())
        
        if "".join(text.split()) != checkstr:
            raise ValueError("params Error")

        paramdict = {}
        for i in params:
            paramdict[i[0]]=True

        relist = {}
        for i in retext:
            if i[0]: 
                param_key = "app_param_"+i[0]  ## maybe helpful
            else:
                if len(params) == 0 :
                    raise IndexError("too many args")
                param_key = params[0][0]
            relist[param_key] = i[1][1:-1]

            if param_key in paramdict:
                del paramdict[param_key]
            #else:
            #    raise IndexError("Unfound param or depucliated param")

        print(relist)
        return relist
    
    def messageSend(self,channel,text):
        #print(text)
        print(
        self.slack.api_call("chat.postMessage",
                channel  = channel,
                username = "KXGEN_BOT",
                icon_url = "https://app.kxg.io/images/logo.png",
                text     =  text)
        )

    def getForm(self,function):
        web = requests.Session().get("https://app.kxg.io/"+function+"/")
        if web.status_code == 404:
            raise ValueError("app not found")
        bs = BS(web.text,"lxml")
        appname = bs.find(id="header_app_title").text 

        appparams = []
        #input
        #print(bs.find("form"))
        for i in bs.find("form").find_all("input"):
            if 'placeholder' in i.attrs:
                appparams.append((i['name'],i['placeholder']))
            elif 'value' in i.attrs:
                appparams.append((i['name'],i['value'      ]))
            else:
                appparams.append((i['name'],"Unknown method"))
        
        #select 
        for i in bs.find("form").find_all("select"):
            selectword  = "\n"
            for option in i.find_all("option"):
                selectword+= "\t"+option['value'] + " = " + option.text+"\n"
            appparams.append( (i['name'],selectword if selectword !='\n' else "Unknown") )

        #textarea
        for i in bs.find("form").find_all("textarea"):
            appparams.append(    (i['name'],i.text or "textarea") )

        return appname,appparams

    def getHelp(self,channel,function="",errorword="help"):
        if not function:
            helptext = "Grab the strange PNGimage from https://app.kxg.io\n"
            helptext+= "Usage: kxgen [function]  [params...]\n"
            helptext+= "Type kxgenhelp [function] to get params details\n"
            self.messageSend(channel,helptext)
            return 
        if errorword != "help":
            self.messageSend(channel,function +" "+ errorword)
        elif function == "list":
            helptext = "Support : "+"classic,profile,charm,board,tpgg,poem,amnesty,bamboobook,springcouplets,apr7,anonymous,jiade,kangxicover,you-are-already-dead,ruifan,interrupt"
            helptext += "\nPartly Support :"+"cover,kickass,quote,wada"
            nosupport = "changyusheng,tree,indiedaadee,snape,tianlongren,haulungpin,kangxi,roc,taiwan,tibet,nylon,monkey,fu,hongkong,president,19head,doge,monalisa,nekomimi,ahss,xdd,iing,burn,windows10,andrejs,apologize,speedline,shining,yee,withnylon"
            self.messageSend(channel,helptext)
        else:
            try:
                name,params = self.getForm(function)
            except ValueError as er:
                self.messageSend(channel,er.__str__())
                return
            except KeyError as er:
                self.messageSend(channel,"This app cannot use by this bot")
                return

            helptext = "app:"+function+"\n"
            helptext+= "appname:"+name+"\n"
            for i in params:
                if i[0].startswith("app_param_"):
                    helptext+= i[0][10:]+":"+i[1]+"\n"
                else:
                    helptext+= i[0]+":"+i[1]+"\n"

            self.messageSend(channel,helptext)
            
    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        text = datadict['text']
        channel = datadict['channel']
        payload = {
                'channels':channel,
                'filename':datadict['ts']}

        if text.startswith("kxgen "):
            data = re.search(r"(?<=kxgen ).*",text,re.DOTALL).group().strip()
            
            try:
                app = data.split()[0]
            except IndexError:
                self.getHelp(channel,"app","not input")
                return 

            try:
                appname,params = self.getForm(app)
            except ValueError as er:
                self.getHelp(channel,app,"Not found")
                return
            data = re.findall(r"^(?:"+app+" *)(.*)",data,re.DOTALL)
            data = data[0] if data else ""

            try:
                param = self.paramParse(data,params)
            except ValueError as er:
                self.getHelp(channel,app,er.__str__())
                return 
            except IndexError as er:
                self.getHelp(channel,app,er.__str__())
                return 

            payload['files'] = {'file':self.pngDownload( app, appname, param)}
            print(self.slack.api_call("files.upload",**payload))

        elif text.startswith("kxgenhelp") or text=="kxgen":
            channel = datadict['channel']
            if text == "kxgenhelp" or text=='kxgen':
                self.getHelp(channel)
            else:
                data = re.search(r"(?<=kxgenhelp) *\w+",text)
                if data:
                    self.getHelp(channel,data.group().strip())
                else:
                    self.getHelp(channel)
            
