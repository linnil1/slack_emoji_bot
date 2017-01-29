from slackclient import SlackClient
import json
import jieba
import re
import os

class FOOD:
    def require():
        return [{"name":"food_channelname","default":"midnight"}]
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
        self.slack = slack
        self.rundata = custom['data']
        self.colorPrint = custom['colorPrint']

        self.food_dir = "data/midnight.json"
        self.food_dic = "data/dict.txt.big"

        #find midnight channel
        self.nochannel = False
        rep = self.slack.api_call("channels.list")
        self.channel_id = ""
        for c in rep['channels']:
            if c['name'].lower() == custom['food_channelname']:
                self.channel_id = c['id']
                break;

        jieba.set_dictionary(self.food_dic)
        jieba.initialize()

        # add and del words
        for word in self.rundata.get('FOOD_addword'):
            jieba.add_word(word)
        for word in self.rundata.get('FOOD_delword'):
            jieba.del_word(word)

        if not self.channel_id:
            self.colorPrint("No midnight channel","Restart when midnight channel can use",color="FAIL")
            self.nochannel = True
            return

        self.init()

    def init(self):
        # cut
        self.img = []
        if os.path.exists(self.food_dir):
            self.imgs = json.loads(open(self.food_dir).read())
            for img in self.imgs:
                img['jieba'] = (jieba.lcut(img['title']))
        open(self.food_dir,"w").write(json.dumps(self.imgs))

        # build
        self.jieba_dic = {}
        for img in self.imgs:
            for jiba in img['jieba']:
                self.jieba_dic[jiba] = img

    def wordSearch(self,text):
        textarr = jieba.lcut(text)
        self.colorPrint("Jieba cut",textarr)
        for t in textarr:
            if t in self.jieba_dic :
                return self.jieba_dic[t]
        raise ValueError("not found")
    def wordParse(self,img):
        return {
            "title": img['title'],
            "title_link": img['permalink'],
            "image_url":img['url_private']
            #cannot use thnum_360 i don't know why
        }

    def imageAdd(self,img):
        self.colorPrint("Add Foods",img)
        img['jieba'] = (jieba.lcut(img['title']))
        for jiba in img['jieba']:
            self.jieba_dic[jiba] = img
        self.img.append(img)
        open(self.food_dir,"w").write(json.dumps(self.imgs))

    def main(self,datadict):
        if self.nochannel:
            return 
        if datadict['type'] == 'message' and datadict.get('subtype') == "file_share" and datadict.get('channel') == self.channel_id :
            self.imageAdd(datadict['file'])
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 
        if datadict['text'].startswith("food "):
            text = re.search(r"(?<=food ).*",datadict['text'],re.DOTALL).group().strip()

            payload = {
                    "username": "食物 Midnight",
                    "icon_emoji": ":_e9_a3_9f:",
                    "thread_ts":datadict.get("thread_ts")or'',
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
            self.rundata.append("FOOD_addword",text)
            self.init()
        elif datadict['text'].startswith("fooddel "):
            text=re.search(r"(?<=fooddel ).*",datadict['text']).group().strip()
            jieba.del_word(text)
            self.rundata.append("FOOD_delword",text)
            self.init()
