#!/usr/bin/python
# -*- coding: utf-8  -*-

from slackclient import SlackClient
from upload_emoji import Emoji
import os
import urllib.request

#need to be delete
slack = SlackClient()
emoji = Emoji()

def emojiDownload(qstr):
    emoji_list = []
    for word in qstr:
        bword = word.encode("utf8")

        webword = ""
        for i in bword:
            webword += "%{0:x}".format(i)
        url = "http://xiaoxue.iis.sinica.edu.tw"
        geturl = url + "/ImageText2/ShowImage.ashx?text="+webword+"&font=%e5%8c%97%e5%b8%ab%e5%a4%a7%e8%aa%aa%e6%96%87%e5%b0%8f%e7%af%86&size=36&style=regular&color=%23000000"
        rep  = urllib.request.urlopen(geturl).read()
        print(len(rep))
        if len(rep)<140:
            print(word+" not found")
            emoji_list.append(word)
            continue

        webword = webword.replace("%","_")
        with open(webword,"wb") as f:
            f.write(rep)
        emoji_list.append(webword)

    return emoji_list

def emoji_message(qstr,channel):
    str_list = emojiDownload(qstr)
    message = ""
    for word in str_list:
        if word[0]=="_":
            emoji.imageUpload(word,word)
            message += ":"+word+":"
        else:
            message += word

    print(slack.api_call("chat.postMessage",channel=channel,text=message))

emoji_message("等等測試小篆圖片轉換器","#random")
