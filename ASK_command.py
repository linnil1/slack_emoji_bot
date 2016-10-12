import requests
import re
from lxml import etree
import urllib

class ASK_wolfram: 
    def __init__(self,slack,custom):
        self.slack = slack
        self.custom = custom
        self.appid = "G9739J-Q39LE43565"

    def answerGet(self,text):
        rep = requests.get("http://api.wolframalpha.com/v2/query?appid="+self.appid+"&input="+urllib.parse.quote(text)+"&format=image,plaintext")

        xml = etree.fromstring(rep.text.encode("UTF8"))

        if not xml.attrib['success'] :
            return False

        # if result is primary, just print as brief answer
        primary = xml.xpath("//*[@primary]")
        if primary:
            answer = []
            scan = xml.xpath("//*[@id='Input']")
            if scan:
                answer.append( {
                    "title":    (scan[0].xpath("*/plaintext")[0].text),
                    'image_url':(scan[0].xpath("*/img")[0].attrib['src']) })
            answer.append( {
                "title":" = "+(primary[0].xpath("*/plaintext")[0].text),
                'image_url':  (primary[0].xpath("*/img")[0].attrib['src']) })

            return answer

        # get all pods
        pods = xml.xpath("//pod")
        podarr= []
        for pod in pods:
            podarr.append({
                'title':(pod.attrib['title']),
                'image_url':(pod.xpath("*/img")[0].attrib['src'])
            })
        return podarr

    def main(self,datadict):
        if datadict['type'] == 'message' and datadict['text'].startswith("ASK "):
            text = re.search(r"(?<=ASK ).*",datadict['text'],re.DOTALL).group().strip()

            payload = {
                "username": "WolframAlpha Answer",
                "icon_emoji": ":_e7_ae_97:",
                "channel": datadict['channel']}

            answer = self.answerGet(text)
            if answer:
                self.slack.api_call("chat.postMessage",**payload,attachments=answer)
            else:
                self.slack.api_call("chat.postMessage",**payload,text="False")

