
from lxml import html
import requests
import re
import dateutil.parser
import datetime
from pprint import pprint

#this is for NTUOSC
class COURSE:
    def require():
        return ["team_name"]
    def __init__(self,slack,custom):
        self.slack = slack
        self.isntuosc = custom['team_name'] == 'ntuosc'
        self.coursedata = []

    def courseAll(self):
        req = requests.get("http://ntuosc.org/courses/")
        tree = html.fromstring(req.text)
        table = tree.xpath("//table")[0]

        tabledata = []
        dicname = []
        ths = table.xpath("thead/tr/th/text()")
        trs = table.xpath("tbody/tr")
        now = datetime.datetime.now()
        for tr in trs:
            dic = {}
            for i,td in enumerate(tr.xpath("td")):
                text = td.text_content().strip()
                if i==0:
                    dic["datetime"] = dateutil.parser.parse(text+" 22:00")
                dic[ ths[i] ] = {
                    "text": text,
                    "link": td.xpath("a")[0].get("href") if td.xpath("a") else ""
                    }
            tabledata.append(dic)

        tabledata.sort(key=lambda a: a['datetime'] )
        #pprint(tabledata)
        self.coursedata = tabledata

    def courseGet(self):
        now = datetime.datetime.now()
        for c  in self.coursedata:
            if c['datetime'] > now:
                return c
        return "no class"

    def courseParse(self):
        dic = self.courseGet()
        print(dic)
        if dic == "no class":
            return "no class"

        text = ""
        for key,dat in dic.items():
            if key != "datetime":
                text += '*' + key + "* : "
                if dat['link']:
                    text += '<'+dat['link']+'|'+dat['text']+ ">\n"
                else:
                    text += dat['text'] + "\n"

        print(text)
        return text

    def main(self,datadict):
        if not self.isntuosc:
            return 
        if not datadict['type'] == 'message' or ('subtype' in datadict and datadict['subtype'] != "bot_message"):
            return 
        if datadict['text'] == "社課":
            self.courseAll() # sync every time
            return self.slack.api_call("chat.postMessage",
                text = self.courseParse(), **{
                    "channel"  : datadict['channel'],
                    "timestamp": datadict['ts'],
                    "username" : "社課 Notify",
                    "icon_emoji": ":_e8_aa_b2:"},
                attachments = [{
                    "title": "Website",
                    "title_link": "http://ntuosc.org/courses/"
                    }]
                )
    
#a = COURSE("","")
#a.courseAll()
#print(a.courseParse())
