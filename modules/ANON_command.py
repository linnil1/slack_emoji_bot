
class ANON:
    def require():
        return [{"name":"channelname"}]
    def __init__(self,slack,custom):
        self.slack = slack
        self.channel = self.channelFind(custom['channelname'])

    def channelFind(self,name):
        rep = self.slack.api_call("channels.list")
        for c in rep['channels']:
            if c['name'].lower() == name:
                return c['id']
        raise ValueError("wrong channel name")

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        if datadict['text'].startswith("anon ") and datadict['channel'].startswith('D'):#direct message
            datadict.update( {
                "username": "匿名者 Anonymouser",
                "icon_emoji": "_e5_8c_bf",
                "channel": self.channel
            } )
            self.slack.api_call("chat.postMessage",**datadict)
