from slackclient import SlackClient
from pprint import pprint
import json
import jieba.analyse
import re

class Midnight:
    def jsonBuild():
        # osc
        slack = SlackClient("")
        custom = SlackClient("")
        nowpage = 1
        imgs = []
        while True:
            rep = custom.api_call("files.list",channel="C045B1Y37",type="images",page=nowpage)
            nowpage += 1
            print(rep)
            imgs.extend(rep['files'])
            if rep['paging']['pages'] <= nowpage:
                break

        imgs.reverse()
        open("midnight.json","w").write(json.dumps(imgs))
    def jiebaWrite():
        jieba.set_dictionary('dict.txt.big')
        imgs = json.loads(open("midnight.json").read())
        for img in imgs:
            img['jieba'] = (jieba.analyse.extract_tags(img['title']))
        open("midnight.json","w").write(json.dumps(imgs))


    def __init__(self,slack,custom):
        self.slack = slack
        self.custom = custom
        imgs = json.loads(open("midnight.json").read())
        self.jieba_dic = {}
        for img in imgs:
            for jiba in img['jieba']:
                self.jieba_dic[jiba] = img
        jieba.initialize()
        print("init done")

    def wordSearch(self,text):
        textarr = jieba.analyse.extract_tags(text)
        print(textarr)
        for t in textarr:
            if t in self.jieba_dic :
                return self.jieba_dic[t]
        raise ValueError("not found")
    def wordParse(self,img):
        print(img)
        return {
            "title": img['title'],
            "title_link": img['url_private'],
            "image_url":img['url_private']
        }

    def test(self):
        while True:
            text  = input()
            ans = {}
            try:
                ans = self.wordSearch(text)
                pprint(self.wordParse(ans))
            except:
                ans = {}


    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 
        if datadict['text'].startswith("food "):
            text = re.search(r"(?<=food ).*",datadict['text'],re.DOTALL).group().strip()

            try:
                ans = self.wordSearch(text)

                self.slack.api_call("chat.postMessage",
                    username="食物 Midnight",
                    icon_emoji= ":_e9_a3_9f:",
                    channel=datadict['channel'],
                    attachments=[self.wordParse(ans)]
                )
            except:
                self.slack.api_call("chat.postMessage",
                    channel=datadict['channel'],
                    username="食物 Midnight",
                    icon_emoji= ":_e9_a3_9f:",
                    text = "Sorry Not Found"
                )
                

