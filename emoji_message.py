#!/usr/bin/python
# -*- coding: utf-8  -*-

from slackclient import SlackClient
from upload_emoji import Emoji
import os
import urllib.request
import urllib.parse
import json

privacy = json.loads(open("privacy.json").read())
slack = SlackClient(privacy['token'])
emoji = Emoji(privacy['team_name'],privacy['email'],privacy['password'])

def emojiDownload(qstr):
    emoji_list = []
    for word in qstr:
        webword = urllib.parse.quote(word).lower()
        url = "http://xiaoxue.iis.sinica.edu.tw"
        geturl = url + "/ImageText2/ShowImage.ashx?text="+webword+"&font=%e5%8c%97%e5%b8%ab%e5%a4%a7%e8%aa%aa%e6%96%87%e5%b0%8f%e7%af%86&size=36&style=regular&color=%23000000"
        rep  = urllib.request.urlopen(geturl).read()
        print("pnglen = "+str(len(rep)))
        if len(rep)<140:
            print(word+" not found")
            emoji_list.append(word)
            continue

        webword = webword.replace("%","_")
        print(word+" -> "+webword)
        with open("word_data/"+webword,"wb") as f:
            f.write(rep)
        emoji_list.append(webword)

    return emoji_list

def emoji_message(qstr,channel):
    str_list = emojiDownload(qstr)
    message = ""
    for word in str_list:
        if word[0]=="_":
            emoji.imageUpload(word)
            message += ":"+word+":"
        else:
            message += word

    print(slack.api_call("chat.postMessage",channel=channel,text=message,username="小篆transformer",icon_emoji=":_e7_af_86:"))

