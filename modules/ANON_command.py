import argparse
import shlex

class ANON:
    def require():
        return [{"name":"channelname"}]
    def __init__(self,slack,custom):
        self.slack = slack
        self.channel = self.channelFind(custom['channelname'])
        self.parser = None
        self.initParse()

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

    def channelFind(self,name):
        rep = self.slack.api_call("channels.list")
        for c in rep['channels']:
            if c['name'].lower() == name:
                return c['id']
        raise ValueError("wrong channel name")

    def personFind(self,name):
        rep = self.slack.api_call("users.list")
        for c in rep['members']:
            if c['name'].lower() == name.lower():
                return {
                    'username': c['name'],
                    'icon_url': c['profile']['image_72'],
                    'icon_emoji': ""  # remove emoji by hacking
                    }
        return {}

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        if datadict['text'].startswith("anon ") and datadict['channel'].startswith('D'):#direct message
            outtext =  {
                "username": "匿名者 Anonymouser",
                "icon_emoji": ":_e5_8c_bf:",
                "channel": datadict['channel']
            } 

            try:
                textin = self.parser.parse_args(shlex.split(datadict['text'][5:]))
                print(textin)

            except SystemExit as er:
                outtext['text']  = "Bad syntax"
                self.slack.api_call("chat.postMessage",**outtext)
                return 

            if textin.help:
                outtext['text'] = "```"+self.parser.format_help()+"```"
                textin = self.parser.parse_args(shlex.split(datadict['text'][5:]))
                self.slack.api_call("chat.postMessage",**outtext)
                return 

            outtext['channel'] = self.channel
            outtext['text'] = ' '.join(textin.msg)
            if textin.who :
                outtext.update(self.personFind(textin.who))

            self.slack.api_call("chat.postMessage",**outtext)
