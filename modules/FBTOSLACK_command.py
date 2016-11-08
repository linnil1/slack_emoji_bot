import facebook 
from datetime import datetime
from pprint import pprint

class FBTOSLACK:
    def __init__(self,slack,custom):
        self.slack = slack
        self.custom = custom
        self.club = ""
        self.since = int(datetime.now().strftime("%s")) 
        self.interval = 10
        self.payload = {
            'channel': "C1W0SLNSC",
            'username': "FB syncer",
            'icon_emoji': ":_e7_89_9b:"
        }
        self.init("")
        self.stop = False

    def init(self,token):
        self.graph = facebook.GraphAPI(access_token=token, version="2.7")


    def attachFind(self,datarr,dep=0):
        attachs = []
        for data in datarr:
            attach = {}
            if data.get('media') and data['media'].get('image'):
                attach['image_url'] = data['media']['image']['src']
                if data['type'] == "video_inline":
                    attach['text'] = "<"+data['url']+"|Click link to see videos>"
                else:
                    attach['text'] = "Images"
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
        return {'attachments':attachs}

    def feedsGet(self):
        try:
            feeds = self.graph.get_object(id=self.club+"/feed", fields="message,attachments,permalink_url,from,story,description,type,created_time",since=self.since)
            self.since = int(datetime.now().strftime("%s"))
        except:
            print("error")
            self.stop = True
            return 
        feeds = feeds['data'] # ignore paging
        pprint(feeds)
        return feeds

    def main(self):
        if self.stop:
            return 
        if  int(datetime.now().strftime("%s")) - self.since < self.interval:
            return 
        feeds = self.feedsGet()
        if not feeds:
            return 

        messages = [ self.feedToSlack(feed) for feed in feeds[-1:0]]
        for message in messages:
            self.slack.api_call("chat.postMessage",**self.payload,**message)
