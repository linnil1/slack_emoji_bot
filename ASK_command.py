import requests
import re
from lxml import etree
from functools import partial

class ASK_wolfram: 
    def __init__(self,slack,custom):
        self.slack = slack
        self.custom = custom
        self.appid = self.custom.wolfram_app

    def apiCall(self,text,assum=""):
        rep = requests.get("http://api.wolframalpha.com/v2/query",
            params= {
                "appid":self.appid,
                "input":text,
                "format":"image,plaintext",
                "assumption":assum})
        print("call "+rep.url)
        return etree.fromstring(rep.text.encode("UTF8")) 

    def assumCall(self,text,num):
        xml = self.apiCall(text)
        assum = xml.xpath("//assumption/value")
        if 0 <= num and num < len(assum):
            return self.apiCall(text,assum[num].attrib['input'])
        else:
            return etree.Element("err",attrib={"success":"Index Error"})

    def warnsGet(self,xml,podarr):
        podarr.append( self.warnGet(xml,"//warnings/*","Reinterpret") )
        podarr.append( self.warnGet(xml,"//tip","Tip") )
        podarr.append( self.warnGet(xml,"//didyoumean","Suggest","inside") )
        podarr.append( self.warnGet(xml,"//languagemsg","Language Error","english") )
        podarr.append( self.warnGet(xml,"//futuretopic","Futuretopic","msg") )

    def warnGet(self,xml,path,name,attr="text"):
        warn = xml.xpath(path)
        if warn:
            dic = {
                "title": name,
                "color": "danger"}
            if attr != "inside" :
                dic["text"]= "\n".join([w.attrib[attr] for w in warn])
            else:
                dic["text"]= "\n".join([w.text for w in warn])
            return dic

        return {}


    def answerGet(self,xml,short=True,showall=False):
        if xml.attrib['success'] != "true" and xml.attrib['success'] != "false":
            return str(xml.attrib['success'])

        # if result is primary, just print as brief answer
        primary = xml.xpath("//*[@primary]")
        if short and primary:
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

        # find warning
        self.warnsGet(xml,podarr)
        
        # find main
        for pod in pods:
            podarr.append({
                'title':(pod.attrib['title']),
                'image_url':(pod.xpath("*/img")[0].attrib['src'])
            })
            # all pic
            if showall:
                podarr.extend([{
                    'text':" ",
                    'image_url':(p.attrib['src'])} for p in pod.xpath("*/img")[1:]])

        # find assumption
        assum = xml.xpath("//assumption/value")
        if assum:
            podarr.append({
                "title": "Did you mean?",
                "color": "warning",
                "text": "\n".join(['['+str(i)+'] '+w.attrib['desc'] for i,w in enumerate(assum)])})

        if not podarr:
            podarr = "False"
        return podarr

    def imgurUse(self,urlarr):
        newarr = self.custom.imgur.imagesUpload([url['image_url'] for url in urlarr])
        for i,newurl in enumerate(newarr):
            urlarr[i]['image_url'] = newurl

    def textOut(self,pat,text):
        return  re.search(pat,text,re.DOTALL).group().strip()

    def main(self,datadict):
        if datadict['type'] == 'message':
            answer = ""
            config = {}
            func = self.apiCall
            if re.search(r"^ASK\[\d+\]",datadict['text']):
                num = int(re.findall(r"^ASK\[(\d+)\]",datadict['text'])[0])
                datadict['text'] = re.sub(r"^ASK\[(\d+)\]","ASK",datadict['text'])
                func=partial(self.assumCall,num=num)

            if datadict['text'].startswith("ASK "):
                text = self.textOut(r"(?<=ASK ).*",datadict['text'])
            elif datadict['text'].startswith("ASKmore "):
                text = self.textOut(r"(?<=ASKmore ).*",datadict['text'])
                config['short'] = False
            elif datadict['text'].startswith("ASKall "):
                text = self.textOut(r"(?<=ASKall ).*",datadict['text'])
                config['short'] = False
                config['showall'] = True

            elif datadict['text'].startswith("ASKhelp"):
                answer="""
`ASK {your question}` Ask wolfram about your question
`ASKmore  {quetsion}` Ask and get more data 
`ASKall   {quetsion}` Ask and get all  data 
If your want to choose the meaning in `Did you mean?`
`ASK[{num}] {question}`
`ASK[{num}]more {question}`
`ASK[{num}]all  {question}`
                """
            else:
                return 

            payload = {
                "username": "WolframAlpha Answer",
                "icon_emoji": ":_e7_ae_97:",
                "channel": datadict['channel']}

            if not answer:
                answer = self.answerGet(func(text),**config)
            if type(answer) is list:
                #self.imgurUse(answer)
                self.slack.api_call("chat.postMessage",**payload,attachments=answer)
            else:
                self.slack.api_call("chat.postMessage",**payload,text=answer)
