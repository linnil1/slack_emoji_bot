
class TRANSLATE:
    def require():
        return [{"name":"Translate","module":"True"}]

    def __init__(self,slack,custom):
        self.slack = slack
        self.translate = custom['Translate'].translate
        self.payload = {
            "username": "翻譯 translator",
            "icon_emoji": ":_e8_ad_af:"
        }

    def parse(self,text):
        arr = text.split(' ')
        opt = {}
        text = []
        for t in arr[1:]:
            if t.startswith("--from="):
                opt['from'] = t[7:]
            elif t.startswith("--to="):
                opt['to'] = t[5:]
            else:
                text.append(t)

        return (' '.join(text),opt)

    def format(self,text):
        #text = text.split('\n')
        #if len(text) != 1:
        #    text = text[0] + "\nLang: "+ text[1]
        #return text
        return text[:text.find('\n')]

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        if datadict['text'].startswith("translate "):
            text,opt = self.parse(datadict['text'])
            print(text,opt)
            try:
                trans = self.format(self.translate(text,opt))
            except ValueError as err:
                trans = err.__str__()
            print(trans)

            self.slack.api_call("chat.postMessage",
                    text = trans,
                    channel = datadict['channel'],
                    **self.payload )
        if datadict['text'] == "translatehelp":
            helptext = """ ```
translate text
translate text --from=en --to=zh-TW ``` """
            self.slack.api_call("chat.postMessage",
                    text = helptext,
                    channel = datadict['channel'],
                    **self.payload )


        
