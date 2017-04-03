from concurrent.futures import ThreadPoolExecutor
import urllib.request
import urllib.parse
import hashlib
import os.path
import string
import re
import time
import math
from PIL import Image

from oldreact_util import oldreact
import oldtime_util


class OLD:
    def require():
        return [{"name": "Emoji", "module": True}]

    def __init__(self, slack, custom):
        self.dir = "data/word_data/"
        self.keyword = "old"
        self.slack = slack
        self.colorPrint = custom['colorPrint']
        self.emoji = custom['Emoji']
        self.oldreact = oldreact(slack, self.colorPrint)

    def wordTofilename(self, word):
        return urllib.parse.quote(word).lower().replace("%", "_")

    def imageDownload(self, word):
        self.colorPrint("Download Image", word)
        webword = urllib.parse.quote(word).lower()
        geturl = "http://xiaoxue.iis.sinica.edu.tw" + \
                 "/ImageText2/ShowImage.ashx?text=" + webword + \
                 "&font=%e5%8c%97%e5%b8%ab%e5%a4%a7%e8%aa%aa%e6%96%87%e5%b0%8f%e7%af%86" + \
                 "&size=36&style=regular&color=%23000000"

        urllib.request.urlretrieve(
            geturl, self.dir + self.wordTofilename(word))

    def wordTomessage(self, word):
        filename = self.wordTofilename(word)
        pnglen = len(open(self.dir + filename, "rb").read())
        self.colorPrint("PNG Size", word + " = " + str(pnglen))
        if pnglen < 140:
            self.colorPrint("Word not found", word, color="OKBLUE")
            return word
        else:
            return ":" + filename + ":"

    def imageProcess(self, word):
        """
        check exist.  Download when not exist
        check image is not blank and change word to emoji syntax.
        if we download good image , upload as emoji
        """
        if word in string.printable:
            # this will not include our target : Chinese
            return word
        filename = self.wordTofilename(word)
        file_noexist = not os.path.isfile(self.dir + filename)
        if file_noexist:
            self.imageDownload(word)
        message = self.wordTomessage(word)
        if file_noexist and len(message) != 1:
            self.colorPrint("Emoji upload", filename + " >> " +
                            self.emoji.upload(self.dir, filename))
        return message

    def imageUpDown(self, qstr):
        uniquestr = list(set(qstr))
        with ThreadPoolExecutor(max_workers=16) as executor:
            unimap = dict(zip(uniquestr, executor.map(
                self.imageProcess, uniquestr)))
            return ''.join([unimap[i] for i in qstr])
    # ---- simple old commmand END----

    def gifTime(self, text):  # default 0.5s
        t = re.findall(r"^-t\s*(.*?)\s+", text)
        if len(t) > 1:
            raise ValueError("Arguments Error")
        elif len(t) == 0:
            return 0.5
        try:
            giftime = float(t[0])
            assert(giftime >= 0)
        except BaseException:
            raise ValueError("time number error")
        if giftime >= 10:
            raise ValueError("time number too big")
        return giftime

    def gifWord(self, data):
        text = self.imageUpDown(data)
        onlyemoji = re.findall(r":(.*?):", text)
        if len(onlyemoji) < 2:
            raise ValueError("Need at least two words")
        if len(onlyemoji) > 100:
            raise ValueError("too many words")
        return onlyemoji

    def gifimageTrans(self, im):  # I don't know how to descripe
        whiteim = Image.new("RGB", im.size, (255, 255, 255))
        whiteim.paste(im, mask=im.split()[3])
        alphaim = whiteim.convert("RGBA")
        datas = alphaim.getdata()
        new_data = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append((item[0], item[1], item[2], 255))
        alphaim.putdata(new_data)
        return alphaim

    def gifMake(self, text):
        giftime = self.gifTime(text) * 1000
        gifword = self.gifWord(text)
        hashname = "oldgif_" + hashlib.md5(
            (str(giftime) + str(gifword)).encode('utf-8')).hexdigest()
        self.colorPrint(
            "GIF data", "time= {}\ngifword= {}".format(giftime, gifword))
        if os.path.isfile(self.dir + hashname):
            return ':' + hashname + ':'

        ims = [self.gifimageTrans(Image.open(self.dir + word))
               for word in gifword]
        ims[0].save(self.dir + hashname,
                    append_images=ims[1:],
                    duration=giftime,
                    disposal=2,
                    loop=0,
                    format="GIF", save_all=True, transparency=0)

        self.colorPrint("Emoji upload", hashname + " >> " +
                        self.emoji.upload(self.dir, hashname))
        return ':' + hashname + ':'

    # ---- gif funtion in this file End ----

    def main(self, datadict):
        self.oldreact.futurereactCount(datadict)
        if datadict['type'] != 'message':
            return
        if 'subtype' in datadict and datadict['subtype'] != "bot_message":
            return

        payload = {
            "channel": datadict['channel'],
            "username": "小篆transformer",
            "thread_ts": datadict.get("thread_ts")or'',
            "icon_emoji": ":_e7_af_86:"}
        text = datadict['text']

        if text.startswith("old "):
            if "'" in text:  # NTUST feature
                payload["text"] = self.imageUpDown(u"「請勿輸入單引號，判定為攻擊！」")
                self.slack.api_call("chat.postMessage", **payload)

            data = re.search(r"(?<=old ).*", text, re.DOTALL).group().strip()
            payload["text"] = self.imageUpDown(data)
            self.slack.api_call("chat.postMessage", **payload)

        elif text.startswith("oldask "):
            data = re.search(r"(?<=oldask ).*", text).group().strip()
            if len(data) == 6:
                udata = "%{}%{}%{}".format(data[0:2], data[2:4], data[4:6])
                data = urllib.parse.unquote(udata)
                payload["text"] = self.imageUpDown(
                    data) + " = " + data + " = " + udata
                self.slack.api_call("chat.postMessage", **payload)

        elif text.startswith("oldreact "):
            data = re.search(r"(?<=oldreact ).*", text,
                             re.DOTALL).group().strip()
            emoji_str = self.imageUpDown(data)
            self.oldreact.main(datadict, emoji_str)

        elif text.startswith("oldset "):
            data = re.search(r"(?<=oldset).*", text, re.DOTALL).group().strip()
            two = re.findall(r"\w+", data)
            if len(two) != 2:
                payload['text'] = "args error"
                self.slack.api_call("chat.postMessage", **payload)
                return
            if len(two[0]) != 1 or two[0] in string.printable:
                payload['text'] = "not 小篆emoji"
                self.slack.api_call("chat.postMessage", **payload)
                return
            transdata = self.imageUpDown(two[0])
            if len(transdata) == 1:
                payload['text'] = "cannot transform to 小篆emoji"
                self.slack.api_call("chat.postMessage", **payload)
                return

            transdata = transdata[1:-1]  # get rid of ::

            payload['text'] = self.emoji.setalias(transdata, two[1])
            self.slack.api_call("chat.postMessage", **payload)

        elif text.startswith("oldhelp"):
            text = """
`old [text]                ` transfer text to 小篆emoji.
`oldask [6characters]      ` To ask what is the chinese word of the url-encoded string
`oldreact (-1) [text]      ` give reactions of 小篆emoji to specific floor(-1) message
`oldset [字] [newName]     ` set alias for 小篆emoji
`oldhelp                   ` get help for the usage of this module
`oldtime (time)            ` show date and time by 小篆emoji
`oldgif (-t 0.5) [text]    ` combine 小篆emojis into 0.5 second per word GIF
`oldgifreact (-1) [text]   ` give reactions of 小篆emoji gif to specific floor message
""".strip()

            self.slack.api_call("chat.postMessage", **payload, text=text)

        elif text.startswith("oldtime"):
            nowtime = ""
            if text == "oldtime":
                nowtime = time.strftime("%Y/%m/%d %H:%M")
            else:
                nowtime = re.search(r"(?<=oldtime ).*", text,
                                    re.DOTALL).group().strip()

            try:
                oldtime_util.setPrint(self.colorPrint)
                nowstr = oldtime_util.timeTostr(nowtime)
            except ValueError:
                return
            payload["text"] = self.imageUpDown(nowstr)
            self.slack.api_call("chat.postMessage", **payload)

        elif text.startswith("oldgif "):
            data = re.search(r"(?<=oldgif ).*", text,
                             re.DOTALL).group().strip()

            try:
                payload['text'] = self.gifMake(data)
            except ValueError as er:
                payload['text'] = self.messagePost(er.__str__())

            self.slack.api_call("chat.postMessage", **payload)

        elif text.startswith("oldgifreact "):
            data = re.search(r"(?<=oldgifreact ).*", text,
                             re.DOTALL).group().strip()
            emoji_str = self.gifMake(data)
            self.oldreact.main(datadict, emoji_str)
