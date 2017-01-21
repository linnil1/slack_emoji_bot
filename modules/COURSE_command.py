
from lxml import html
import requests
import re
import dateutil.parser
import datetime
from pprint import pprint

#this is for NTUOSC
class COURSE:
    def require():
        return [{"name":"team_name"},
                {"name":"course_url"},
                {"name":"course_table_index"},
                {"name":"meet_table_index"}]
    def __init__(self,slack,custom):
        self.slack = slack
        self.isntuosc = custom['team_name'] == 'ntuosc'
        self.url = custom['course_url']
        self.courseIndex = int(custom['course_table_index'])
        self.meetIndex = int(custom['meet_table_index'])
        self.coursedata = []

    def courseGet(self):
        req = requests.get(self.url)
        tree = html.fromstring(req.text)
        return tree.xpath("//*[@class='ace-table']")[self.courseIndex]

    def meetGet(self):
        req = requests.get(self.url)
        tree = html.fromstring(req.text)
        return tree.xpath("//*[@class='ace-table']")[self.meetIndex]

    def courseAll(self,table):
        tabledata = []
        dicname = []
        now = datetime.datetime.now()
        for tr in table.xpath("*/tr"):
            dic = {}
            tds = tr.xpath("td")
            dic["datetime"] = dateutil.parser.parse(tds[0].text_content().strip()+" 22:00")
            dic['data' ] = "\n".join( [td.text_content().strip() for td in tds ] )
            tabledata.append(dic)

        tabledata.sort(key=lambda a: a['datetime'] )
        pprint(tabledata)
        self.coursedata = tabledata

    def courseChoose(self):
        now = datetime.datetime.now()
        for c  in self.coursedata:
            if c['datetime'] > now:
                return c
        return "no class"

    def courseParse(self):
        dic = self.courseChoose()
        if dic == "no class":
            return "no class"

        text = dic['data']
        return text

    def main(self,datadict):
        if not self.isntuosc:
            return 
        if not datadict['type'] == 'message' or ('subtype' in datadict and datadict['subtype'] != "bot_message"):
            return 
        if datadict['text'] in  ["社課","社聚"] :
            if datadict['text'] == "社課":
                self.courseAll(self.courseGet()) # sync every time
            elif datadict['text'] == "社聚":
                self.courseAll(self.meetGet()  ) # sync every time

            return self.slack.api_call("chat.postMessage",
                text = self.courseParse(), **{
                    "channel"  : datadict['channel'],
                    "timestamp": datadict['ts'],
                    "thread_ts":datadict.get("thread_ts")or'',
                    "username" : "社課社聚 Reminder",
                    "icon_emoji": ":_e8_aa_b2:"},
                attachments = [{
                    "title": "Website",
                    "title_link": self.url
                    }]
                )
    
#a = COURSE("",{"team_name":"ntuosc","course_url":"https://paper.dropbox.com/doc/1051-gH1ZIXlAM9wO6nP6hqigX","course_table_index":"0","meet_table_index":"1"})
#a.courseAll(a.courseGet())
#print(a.courseParse())
#a.courseAll(a.meetGet())
#print(a.courseParse())
