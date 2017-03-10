import facebook 
from datetime import datetime
import os
from threading import Timer
import requests

class FBTOSLACK:
    def require():
        return [{"name":"fb_clubid"},
                {"name":"_postman","other":True},
                {"name":"fb_token","default":""},
                {"name":"syncfb_interval","default":60},
                {"name":"sync_auto","default":'True'},
                {"name":"sync_hashtag","default":"#SyncToSlack"},
                {"name":"syncfb_channel","default":"random"}]
    def __init__(self,slack,custom):
        self.slack = slack
        self.colorPrint = custom['colorPrint']
        self.club = custom['fb_clubid']
        self.interval = int(custom['syncfb_interval']) #unit: second
        self.hashtag = custom['sync_hashtag']
        self.auto = custom['sync_auto'] == "True"
        self.diff = 5  # the difference between fb and my time
        self.retry = 5 # retry for error response

        # find broadcast channel
        self.channelname = custom['syncfb_channel']
        
        # find token user 
        self.username = custom['_postman']
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
        self.stop = 5 
        self.messagePost()

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
        rep = self.slack.api_call("users.list")
        for c in rep['members']:
            if c['name'] == self.username:
                rep = self.slack.api_call("im.open",user=c['id'])
                return rep['channel']['id']
        raise ValueError("User for asking token not found")

    def attachFind(self,datarr):
        attachs = []
        for data in datarr:
            attach = {}
            if data.get('description'):
                attach['text'] = data['description'] + "\n"
            else:
                attach['text'] = ""

            linkname = "Link"
            if data.get('media') and data['media'].get('image'):
                attach['image_url'] = data['media']['image']['src']
                if data['type'] == "video_inline":
                    linkname = "Click link to see videos"
                else:
                    linkname = "Image"
            if data.get('url') and ('image_url' in attach or 'description' in data):
                # It cannot be footer because the link may be big
                attach['text'] += "<{}|{}>".format(data['url'], linkname)

            attachs.append(attach)

            #look like recursive
            if data.get('subattachments'):
                attachs.extend(self.attachFind(data['subattachments']['data']))
        return attachs

    def pagingAll(self,data):
        def pagingGo(data):
            get_data = data
            while True:
                if get_data.get('data'):
                    yield get_data['data']
                if not get_data['paging'].get('next'):
                    break
                get_data = requests.get(get_data['paging']['next']).json()
        l = []
        for li in pagingGo(data):
            l.extend(li)
        return l

    def feedToSlack(self,feed):
        if feed['id'] in self.rundata.get("fbid"):
            return {} # empty will not output
        self.colorPrint("FB data",feed)

        #hashtag
        # in comments
        who = None
        if self.auto == False and feed.get('comments'):
            #this cannont use for Page 
            for comment in self.pagingAll(feed['comments']):
                if comment.get('message') and \
                   comment['message'].find(self.hashtag) >= 0:
                    who = comment['from']
                    break

        # in message in post data
        if feed.get('message'): 
            # sync when hashtag not found
            if self.auto == True  and feed['message'].find(self.hashtag) ==-1:
                who = feed['from']
            # sync when hashtag found
            if self.auto == False and feed['message'].find(self.hashtag) >= 0:
                who = feed['from']
        # BUG: cannot deal with blank post with plaintext share post
        if not who:
            return {} # empty will not output
        self.colorPrint("Need Shared")
        
        # main text
        main = {}
        main['username'] = feed['from']['name']
        main['icon_url'] = self.graph.get_object(feed['from']['id']+"/picture")['url']
        main['text']=""
        if feed.get('story'):
            main['text'] += '_'+feed.get('story')+"_\n"
        if feed.get('message'):
            main['text'] += feed.get('message') + "\n"

        # attachments
        attachs = []
        if feed.get('attachments'):
            attachs = self.attachFind(feed['attachments']['data'])
            attachs = list(filter(None,attachs))

        attachs.append({'footer':"{}\n<{}|FB_link>".format(
                                 feed['created_time'],feed['permalink_url']),
                        'text'  :"_<https://www.facebook.com/{}|{}> " 
                                 "share to slack_".format(who['id'], who['name']),
                        'mrkdwn_in':["text"] })

        #record fbid for not deplicated post same data
        self.rundata.append("fbid",feed['id'])
        return {**main,'attachments':attachs}

    def feedsGet(self):
        try:
            feeds = self.graph.get_object(
                id    =self.club + "/feed",
                fields="message,attachments,permalink_url,from,story"
                       ",description,type,created_time,comments",
                since =self.rundata.get("timelog")-self.diff)
            self.rundata.set("timelog",int(datetime.now().strftime("%s")))
            self.timerSet(self.interval)
            self.stop = 5
        except:
            self.stop = self.stop-1 
            self.colorPrint("Cannot connect to FB",color="FAIL")
            if self.stop < 0:
                self.colorPrint("STOP FB connection",color="FAIL")
                self.slack.api_call("chat.postMessage",**self.payload_user,text="Token Expired\nUse token=xxx to retoken")
            else:
                self.timerSet(self.retry)
            return 

        feeds = feeds['data'] # ignore paging
        return feeds

    def messagePost(self):
        feeds = self.feedsGet()
        if not feeds:
            return 

        messages = [ self.feedToSlack(feed) for feed in reversed(feeds) ]
        for message in messages:
            self.slack.api_call("chat.postMessage",channel=self.channelname,**message)

    def main(self,datadict):
        # get token
        if datadict['type'] == 'message' and datadict['channel'] == self.payload_user['channel'] and datadict['text'].startswith("token="):
            self.init(datadict['text'][6:])
            

