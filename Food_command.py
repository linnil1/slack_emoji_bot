from slackclient import SlackClient
from pprint import pprint
import json
import jieba
import re

class Midnight:
    def pageParse(t=0):
        custom = SlackClient("")
        nowpage = 1
        imgs = []
        while True:
            rep = custom.api_call("files.list",channel="C045B1Y37",type="images",page=nowpage,ts_from=t)
            nowpage += 1
            print(rep)
            rep['files'].reverse()
            imgs.extend(rep['files'])
            if rep['paging']['pages'] < nowpage:
                break
        imgs.reverse()
        return imgs

    def jsonBuild():
        try: open("midnight.json")
        except: open("midnight.json","w").write(json.dumps({}))
        imgs = json.loads(open("midnight.json").read())
        fid = []
        for f in imgs:
            fid.append( f['id'] )
        imgs.extend([f for f in pageParse() if f not in fid])
        open("midnight.json","w").write(json.dumps(imgs))

    def __init__(self,slack,custom):
        try: open("midnight.json")
        except: print("no json data")
        self.slack = slack
        self.custom = custom
        self.img = []
        jieba.set_dictionary('dict.txt.big')
        jieba.initialize()

        # add and del words
        try: open("words.jb")
        except: open("words.jb","w")
        for word in list(filter(None,open("words.jb").read().split('\n'))):
            if word[0] == '+' : 
                jieba.add_word(word[1:])
            elif word[0] == '-' : 
                jieba.del_word(word[1:])
        self.init()

        #find midnight channel
        rep = self.slack.api_call("channels.list")
        self.channel_id = ""
        for c in rep['channels']:
            if c['name'].lower() == 'midnight':
                self.channel_id = c['id']
                break;

        if not self.channel_id:
            print("no midnight channel")
            raise ValueError

        print("init done")

    def init(self):
        # cut
        self.imgs = json.loads(open("midnight.json").read())
        for img in self.imgs:
            img['jieba'] = (jieba.lcut(img['title']))
        open("midnight.json","w").write(json.dumps(self.imgs))

        # build
        self.jieba_dic = {}
        for img in self.imgs:
            for jiba in img['jieba']:
                self.jieba_dic[jiba] = img

    def wordSearch(self,text):
        textarr = jieba.lcut(text)
        print(textarr)
        for t in textarr:
            if t in self.jieba_dic :
                return self.jieba_dic[t]
        raise ValueError("not found")
    def wordParse(self,img):
        print(img)
        return {
            "title": img['title'],
            "title_link": img['permalink'],
            "image_url":img['url_private']
            #cannot use thnum_360 i don't know why
        }

    def imageAdd(self,img):
        print("midnight add")
        img['jieba'] = (jieba.lcut(img['title']))
        for jiba in img['jieba']:
            self.jieba_dic[jiba] = img
        self.img.append(img)
        open("midnight.json","w").write(json.dumps(self.imgs))

    def main(self,datadict):
        if datadict['type'] == 'message' and datadict.get('subtype') == "file_share" and datadict.get('channel') == "C045B1Y37":
            self.imageAdd(datadict['file'])
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 
        if datadict['text'].startswith("food "):
            text = re.search(r"(?<=food ).*",datadict['text'],re.DOTALL).group().strip()

            payload = {
                    "username": "食物 Midnight",
                    "icon_emoji": ":_e9_a3_9f:",
                    "channel": datadict['channel']}

            try:
                ans = self.wordSearch(text)

                self.slack.api_call("chat.postMessage",
                    attachments=[self.wordParse(ans)],
                    **payload
                )
            except:
                self.slack.api_call("chat.postMessage",
                    text = "Sorry Not Found",
                    **payload
                )
        
        elif datadict['text'].startswith("foodadd "):
            text=re.search(r"(?<=foodadd ).*",datadict['text']).group().strip()
            jieba.add_word(text)
            open("words.jb","w+").write('+'+text+'\n')
            self.init()
        elif datadict['text'].startswith("fooddel "):
            text=re.search(r"(?<=fooddel ).*",datadict['text']).group().strip()
            jieba.del_word(text)
            open("words.jb","w+").write('-'+text+'\n')
            self.init()
                


