import requests 
import shutil
import urllib.parse

class LATEX: 
    def require():
        return [{"name":"Imgur","module":True}]

    def __init__(self,slack,custom):
        self.slack = slack
        self.imgur = custom['Imgur']

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 
        if not datadict['text'].startswith("latex "):
            return 
        oritext = datadict['text'][6:]

        text = urllib.parse.quote(oritext)
        link = self.imgur.imageUpload("https://latex.codecogs.com/gif.latex?"+text)
        print(link)
        self.slack.api_call("chat.postMessage", **{
            "username": "Latex Image",
            "icon_emoji": ":_e7_ae_97:",
            "thread_ts":datadict.get("thread_ts") or '',
            "channel": datadict['channel']},
            attachments = [{
                "title": oritext,
                "image_url":link
            }]
        )

