import facebook 
from datetime import datetime
from pprint import pprint
import os
from threading import Timer

class FBTOSLACK:
    def require():
        return [{"name":"fb_clubid"},
                {"name":"slack_username"},
                {"name":"fb_token","default":""},
                {"name":"syncfb_interval","default":60},
                {"name":"syncfb_channel","default":"random"}]
    def __init__(self,slack,custom):
        self.slack = slack
        self.club = custom['fb_clubid']
        self.interval = int(custom['syncfb_interval']) #unit: second
        self.diff = 5  # the difference between fb and my time
        self.retry = 5 # retry for error response

        # find broadcast channel
        self.channelname = custom['syncfb_channel']
        self.payload = {
            'channel': self.channelFind(),
            'username': "FB syncer",
            'icon_emoji': ":_e5_90_8c:"
        }
        
        # find token user 
        self.username = custom['slack_username']
        self.payload_user = {
            'channel': self.userFind(),
            'username': "FB syncer",
            'icon_emoji': ":_e5_90_8c:"
        }

        # fine sync time
        self.rundata = custom['data']
        if not self.rundata.get("timelog"):
            self.rundata.set("timelog",int(datetime.now().strftime("%s")) )

        self.init(custom['fb_token'])

    def init(self,token):
        self.graph = facebook.GraphAPI(access_token=token, version="2.7")
        self.timerSet(self.interval)
        self.stop = 5 

    def timerSet(self,interval):
        timer = Timer(interval,self.messagePost)
        timer.start()

    def channelFind(self):
        rep = self.slack.api_call("channels.list")
        for c in rep['channels']:
            if c['name'].lower() == self.channelname:
                return c['id']
        raise ValueError("wrong channel name")

    def userFind(self):
        userid = ""
        rep = self.slack.api_call("users.list")
        for c in rep['members']:
            if c['name'] == self.username:
                userid = c['id']
                break
        rep = self.slack.api_call("im.open",user=userid)
        return rep['channel']['id']

    def attachFind(self,datarr,dep=0):
        attachs = []
        for data in datarr:
            attach = {}
            if data.get('media') and data['media'].get('image'):
                attach["title"] = "Images"
                attach['image_url'] = data['media']['image']['src']
                if data['type'] == "video_inline":
                    attach['text'] = "<"+data['url']+"|Click link to see videos>"
                else:
                    attach['text'] = "Image"
                attach['dep'] = dep

            attachs.append(attach)

            #look like recursive
            if data.get('subattachments'):
                attachs.extend(self.attachFind(data['subattachments']['data'],dep+1))
        return attachs

    def feedToSlack(self,feed):
        # main text
        main = {}
        main['author_name'] = feed['from']['name']
        main['author_link'] = "https://www.facebook.com/"+feed['from']['id']

        main['text']=""
        if feed.get('story'):
            main['text'] += '_'+feed.get('story')+"_\n"
            main['mrkdwn_in'] = ["text"]
        if feed.get('message'):
            main['text'] += feed.get('message')

        # attachments
        attachs = []
        if feed.get('attachments'):
            attachs = self.attachFind(feed['attachments']['data'])
            attachs    = list(filter(None,   attachs))
            for attach in attachs:
                if attach['dep'] == 0:
                    attach['color']="#0c0c0c"
                del attach['dep']
            if feed.get('description'):
                attachs.insert(0,{'text':feed['description'],'color':"#0c0c0c"})
            
        attachs = [main]+attachs
        attachs[-1]['footer'] = feed['created_time'] + "'\n<"+feed['permalink_url']+"|FB_link>"

        if feed['id'] in self.rundata.get("fbid"):
            return {} # empty will not output
        else:
            #record fbid for not deplicated post same data
            self.rundata.append("fbid",feed['id'])
            return {'attachments':attachs}

    def feedsGet(self):
        try:
            feeds = self.graph.get_object(id=self.club+"/feed", fields="message,attachments,permalink_url,from,story,description,type,created_time",since=self.rundata.get("timelog")-self.diff)
            self.rundata.set("timelog",int(datetime.now().strftime("%s")))
            self.timerSet(self.interval)
            self.stop = 5
        except:
            self.stop = self.stop-1 
            print("error")
            if self.stop < 0:
                self.slack.api_call("chat.postMessage",**self.payload_user,text="Token Expired\nUse token=xxx to retoken")
            else:
                self.timerSet(self.retry)
            return 

        feeds = feeds['data'] # ignore paging
        if feeds:
            pprint(feeds)
        return feeds

    def messagePost(self):
        feeds = self.feedsGet()
        print(feeds)
        if not feeds:
            return 

        messages = [ self.feedToSlack(feed) for feed in reversed(feeds)]
        for message in messages:
            self.slack.api_call("chat.postMessage",**self.payload,**message)

    def main(self,datadict):
        # get token
        if datadict['type'] == 'message' and datadict['channel'] == self.payload_user['channel'] and datadict['text'].startswith("token="):
            self.init(datadict['text'][6:])
            

