import argparse
import shlex
import requests
import shutil

class ANON:
    def require():
        return [{"name":"channelname"},
                {"name":"Imgur","module":True},
                {"name":"_TOKEN","other":True}]
    def __init__(self,slack,custom):
        self.slack = slack
        self.imgur = custom['Imgur']
        self.token = custom['_TOKEN']
        self.colorPrint = custom['colorPrint']
        self.parser = None
        self.initParse()
        self.payload = {
            "username": "匿名者 Anonymouser",
            "icon_emoji": ":_e5_8c_bf:",
            "channel": '#'+custom['channelname']} 

    def initParse(self):
        self.parser = argparse.ArgumentParser(
            prog="anon",
            description=("Be a anonymous"),
            conflict_handler='resolve'
        )

        self.parser.add_argument('msg',
                            help=("The message you want to post to channel"),
                            type=str, 
                            nargs='*',
                            )

        self.parser.add_argument('--who',
                            help=("Who you want to show on Slack message"),
                            type=str
                            )
        
        self.parser.add_argument('-h','--help',
                            help=("Get help"),
                            action="store_true"
                            )

    def personFind(self,name):
        rep = self.slack.api_call("users.list")
        for c in rep['members']:
            if c['name'].lower() == name.lower():
                return {
                    'username': c['name'],
                    'icon_url': c['profile']['image_72'],
                    'icon_emoji': ""  # remove emoji by hacking
                    }
        self.colorPrint("Person not Find",name,color="WARNING")
        return {}

    def imgDownload(self,url,name):
        #save
        rep = requests.get(url,
                headers={'Authorization':'Bearer '+self.token},
                stream = True)
        path = 'data/tmp/'+name
        if rep.status_code == 200:
            with open(path, 'wb') as f:
                rep.raw.decode_content = True
                shutil.copyfileobj(rep.raw, f)        
        self.colorPrint("Save Image",path)

        #upload
        return self.imgur.pathUpload(path)

    def main(self,datadict):
        if datadict['type'] != 'message' or \
                ( 'subtype' in datadict and datadict['subtype'] != 'file_share' ):
            return 

        if datadict.get('subtype') == 'file_share':
            datadict['text'] = datadict['file']['title'] # make it easy
        
        if datadict['text'].startswith("anon ") and \
                datadict['channel'].startswith('D'):#direct message

            try:
                textin = self.parser.parse_args(shlex.split(datadict['text'][5:]))
                self.colorPrint("Input data",textin)

            except SystemExit as er:
                self.slack.api_call("chat.postMessage",**self.payload,text="Bad syntax")
                return 

            if textin.help:
                outtext = "```"+self.parser.format_help()+"```"
                self.slack.api_call("chat.postMessage",**self.payload,text = outtext)
                return 

            outtext = dict(self.payload)
            if datadict.get('subtype') == 'file_share':
                url = datadict['file']['url_private']
                name = datadict['file']['id']
                url = self.imgDownload(url,name)
                outtext['text'] = "<{}|{}>".format(url,' '.join(textin.msg))
            else:
                outtext['text'] = ' '.join(textin.msg)
            if textin.who :
                outtext.update(self.personFind(textin.who))

            self.slack.api_call("chat.postMessage",**outtext)
