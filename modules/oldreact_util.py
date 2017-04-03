from concurrent.futures import ThreadPoolExecutor, wait
import re


class oldreact:
    def __init__(self, slack, colorPrint):
        self.slack = slack
        self.colorPrint = colorPrint
        self.futurereact = []
        # [ {payload,target,text} ]

    def historyIDGet(self, want, datadict):
        if datadict.get("thread_ts"):
            resp = self.slack.api_call(
                "channels.history",
                channel=datadict['channel'],
                count=1,
                latest=datadict['thread_ts'],
                inclusive=1
            )
            rep = resp['messages'][0]['replies']
            self.colorPrint("Thread History", rep)
            if len(rep) > want:
                return {"channel": datadict['channel'],
                        "timestamp": rep[len(rep) - 1 - want]['ts']}
            else:  # error
                raise ValueError("Floor not found")
        else:
            rep = []
            ts, include = datadict['ts'], 1
            while len(rep) <= want:
                resp = self.slack.api_call(
                    "channels.history",
                    channel=datadict['channel'],
                    count=32,
                    latest=ts,
                    inclusive=include)['messages']

                # filter thread
                for r in resp:
                    if not r.get("thread_ts") or r['thread_ts'] == r['ts']:
                        rep.append(r)

                # continue get history
                ts, include = resp[-1]['ts'], 0
            self.colorPrint("History", [r['text'] for r in rep if r['text']])
            target = rep[want]
            if 'subtype' in target:
                if target['subtype'] == "file_comment":
                    return {"file_comment": target['comment']['id']}
                if target['subtype'] == "file_share":
                    return {"file": target['file']['id']}
            return {"channel": datadict['channel'], "timestamp": target['ts']}

    def floorGet(self, data):
        """ It should be separated by space and the range is [-F,F] in hex """
        strdig = re.search(r"^-?[0-9a-fA-F]+\s", data)
        try:
            dig = int(strdig.group(), 16)
        except ValueError:  # nonetype or strange dig
            raise ValueError("Floor number Error. It should be [-F~F]")

        self.colorPrint("Floor", dig)
        if dig < -0xF or dig > 0xF:
            raise ValueError(str(dig) + " is too big. It should be [-F~F]")
        return dig

    def futurereactCount(self, datadict):
        if datadict['type'] != 'message':
            return
        if not self.futurereact:
            return
        # if not in ["me_message","message_changed","message_deleted"]:
        # if deleted will cause some count error
        # but i don't want to deal it
        with ThreadPoolExecutor(max_workers=16) as executor:
            pool = [executor.submit(self.historyIDGet, f['floor'], datadict)
                    for f in self.futurereact]
            newreact = []
            for i, f in enumerate(self.futurereact):
                if pool[i].result() == f['target']:
                    self.reactSend(self.historyIDGet(0, datadict), f['text'])
                else:
                    newreact.append(f)
            self.futurereact = newreact
        self.colorPrint("future reaction", self.futurereact)

    def futurereactAdd(self, payload, text, floor):
        ch = payload['channel']
        target = self.historyIDGet(0, payload)  # it self
        self.futurereact.append({
            "text": text,
            "target": target,
            "floor": floor
        })
        self.colorPrint("future reaction", self.futurereact)
        self.reactSend(target, ":_e8_a1_8c:")  # ok in Chinese

    def reactSend(self, payload, string):
        with ThreadPoolExecutor(max_workers=16) as executor:
            pool = [executor.submit(
                self.slack.api_call, "reactions.add",
                **payload, name=emoji)
                for emoji in re.findall(r":(\w+):", string)]
            wait(pool)

    def main(self, datadict, emoji_str):
        floor = -1
        futuretext = emoji_str
        try:  # if floor information exist
            if re.search(r"^-?[0-9a-fA-F]+\s", emoji_str):
                floor = self.floorGet(emoji_str)
                futuretext = re.search(
                    r"( .*)", emoji_str, re.DOTALL).group().strip()
        except ValueError as err:
            self.colorPrint("Floor ERR", str(err), color="ERR")
            self.reactSend(self.historyIDGet(0, datadict),
                           ":_e4_b8_8d:")  # No in Chinese
            return
        if floor > 0:
            self.futurereactAdd(datadict, futuretext, floor)
        else:
            self.reactSend(self.historyIDGet(-floor, datadict), emoji_str)
