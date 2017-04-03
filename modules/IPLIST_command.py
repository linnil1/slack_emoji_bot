import requests


class IPLIST:
    def require():
        return [{"name": "team_name"}]

    def __init__(self, slack, custom):
        self.slack = slack
        self.isntuosc = custom['team_name'] == 'ntuosc'
        self.colorPrint = custom['colorPrint']

    def main(self, datadict):
        if not self.isntuosc:
            return
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return

        if datadict['text'] == "iplist":
            payload = {
                "username": "IP位址 lister",
                "icon_emoji": ":_e5_9d_80:",
                "thread_ts": datadict.get("thread_ts") or '',
                "channel": datadict['channel']}
            data = requests.get("https://home.ntuosc.org/go/list/").json()
            self.colorPrint("list", data)
            try:
                s = "\n".join(
                    ["`{}` {}".format(li['IP']['Data'], li['Name']['Data'])
                        for li in data['Device']])
            except BaseException:
                s = "None"
            self.slack.api_call("chat.postMessage", **payload, text=s)
