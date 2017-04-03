import requests
import shutil
import urllib.parse


class LATEX:
    def require():
        return [{"name": "Imgur", "module": True}]

    def __init__(self, slack, custom):
        self.slack = slack
        self.imgur = custom['Imgur']
        self.colorPrint = custom['colorPrint']

    def main(self, datadict):
        if not (datadict['type'] == 'message' and
                datadict.get('subtype') == 'file_share' and
                datadict['file']['filetype'] == 'latex'):
            return
        oritext = datadict['file']['preview']
        text = urllib.parse.quote(oritext)
        link = self.imgur.imageUpload(
            "https://latex.codecogs.com/gif.latex?" + text)
        self.colorPrint("text & image", [text, link])
        self.slack.api_call("chat.postMessage", **{
            "username": "Latex Image",
            "icon_emoji": ":_e7_ae_97:",
            "thread_ts": datadict.get("thread_ts") or '',
            "channel": datadict['channel']},
            attachments=[{
                "title": oritext,
                "image_url": link
            }]
        )
