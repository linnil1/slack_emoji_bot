from lxml import html
import requests
import re
import dateutil.parser
import datetime
from pprint import pprint

#this is for NTUOSC
class COURSE:
    def require():
        return [{"name":"team_name"},{"name":"actid"}]
    def __init__(self,slack,custom):
        self.slack = slack
        self.isntuosc = custom['team_name'] == 'ntuosc'
        self.actid = custom['actid']
        self.colorPrint = custom['colorPrint']
        self.coursedata = []
        self.placedata = []

    def courseAll(self):
        req = requests.get("http://ntuosc.org/courses/")
        tree = html.fromstring(req.text)
        table = tree.xpath("//table")[0]

        tabledata = []
        dicname = []
        ths = table.xpath("thead/tr/th/text()")
        trs = table.xpath("tbody/tr")
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
        self.colorPrint("Table",tabledata)
        self.coursedata = tabledata
        return tabledata

    def placeAll(self):
        if not self.actid:
            return []
        req = requests.get("http://host.cc.ntu.edu.tw/activities/activityDisplay.aspx?Act_ID="+self.actid)
        tree = html.fromstring(req.text)
        table = tree.xpath("//*[@id='resultGrid']")[0]

        tabledata = []
        trs = table.xpath("tr")
        for tr in trs[1:]:
            tds = [td.text_content().strip() for td in tr.xpath("td")]
            print(tds)
            dic = {
                "datetime": dateutil.parser.parse(tds[3]+" 22:00"),
                "日期": tds[3],
                "建物": tds[1],
                "教室": tds[0],
            }
            tabledata.append(dic)

        tabledata.sort(key=lambda a: a['datetime'] )
        self.colorPrint("Table",tabledata)
        self.placedata = tabledata
        return tabledata

    def courseGet(self,data):
        now = datetime.datetime.now()
        for c  in data:
            if c['datetime'] > now:
                return c
        return {}

    def courseParse(self,data):
        dic = self.courseGet(data)
        if not dic:
            return 

        text = ""
        for key,dat in dic.items():
            if key != "datetime":
                text += '*' + key + "* : "
                if isinstance(dat, str):
                    text += dat + '\n'
                elif dat.get('link'):
                    text += '<'+dat['link']+'|'+dat['text']+ ">\n"
                else:
                    text += dat['text'] + "\n"
        return text

    def main(self,datadict):
        if not self.isntuosc:
            return 
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        if datadict['text'] in ["社課"]:#,"社聚"] :
            payload = {
                "username": "社課 Reminder",
                "icon_emoji": ":_e8_aa_b2:",
                "thread_ts":datadict.get("thread_ts") or '',
                "channel": datadict['channel']}

             # sync every time
            text = self.courseParse(self.courseAll())
            if not text: # course data is not newest
                text = self.courseParse(self.placeAll())
            return self.slack.api_call("chat.postMessage",
                    **payload,
                    text = text or "Not Found",
                    attachments = [{
                        "title": "NTUOSC COURSE",
                        "title_link": "http://ntuosc.org/courses/"
                        }]
                    )
    
#a = COURSE("",{"team_name":"ntuosc","colorPrint":lambda a,b:pprint(b),"actid":"85046"})
#a.courseAll()
#a.placeAll()
#print( a.courseParse( a.coursedata ) )
#print( a.courseParse( a.placedata ) )
