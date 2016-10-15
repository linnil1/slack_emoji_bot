from multiprocessing import Pool
import requests
from lxml import html
import re
import random
from urllib.request import urlretrieve
from collections import Counter
import time

def randomGet(dig):
    pool = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghijklmnopqrstuvwxyz"
    ran = ""
    for i in range(dig):
        ran += random.choice(pool)
    return ran

def urlGet(data,delays):
    # get WH
    WH = requests.get('http://gifcreator.me/GetImgWH.php',
            params=data)
    print(WH.text)
    wh = WH.text.split(',')
    #if wh[0]=='1'

    #get url
    GIF = requests.post("http://gifcreator.me/MakeGIF.php",
            data={
                **data,
                'W':wh[1],
                'H':wh[2],
                'Num':str(len(delays)),
                'Order':''.join(delays)})
    print(GIF.text)
    gif = GIF.text.split(',')
    #if gif[0]=='100'
    url = "http://gifcreator.me/download/{}-{}-{}/www.GIFCreator.me_{}.gif".format(
            data['date'][:8],data['date'][8:],data['folder'],gif[1])
    return url

def fileUpload(path,data,name,slep=0):
    time.sleep(slep*0.1)
    while True:
        UP = requests.post(
                "http://gifcreator.me//upload.php",
                #"http://httpbin.org/post",
                data={
                    'name':name+'.png',
                    **data},
                files={
                    'file': (name+'.png', 
                        open(path+name, 'rb'),
                        'image/png')})
        print(UP.text)
        up = UP.json()
        if up['Result'] == 2189 :
            break
        time.sleep(0.1)

    return up['IDBegin']

def filesUpload(path,data,arrs):
    """ beacuse its database is weird ,
        if i upload simuatously , it may give me same index """
    with Pool(processes=len(arrs)) as pool:
       args = [ (path,data,e,i) for i,e in enumerate(arrs)]
       indexs  = pool.starmap(fileUpload,args)
    
    # find if give me same index
    count = Counter(indexs)
    newarr= []
    for i,ind in enumerate(indexs):
        if count[ind] != 1:
            newarr.append(arrs[i])
            indexs[i] = -1

    #reupload my img
    if newarr:
        newindex = filesUpload(path,data,newarr)
        for newind in newindex:
            indexs[ indexs.index(-1) ]  = newind

    return indexs

def gifGet(emojis,delay,path,name):
    print(emojis)
    #get the date // it is yyyymmddhh 
    rep  = requests.get("http://gifcreator.me/")
    page = html.fromstring(rep.text)
    data = {
       'date' : re.findall("\d+",page.xpath("script")[4].text)[0],
       'folder_name' : randomGet(16) }
    data['folder'] = data['folder_name']
    print(data)
    
    #upload
    indexs = filesUpload(path,data,emojis)
    #indexs = []
    #for e in emojis:
    #    indexs.append(fileUpload(path,data,e))
    print(indexs)

    delays = []
    for i in indexs:
        delays.append("{}_{}_".format(i,delay))
    
    #download
    url = urlGet(data,delays)
    print(url)
    urlretrieve(url,path+name)

#gifGet(['_e4_b8_80', '_e4_ba_8c', '_e4_b8_89', '_e5_9b_9b', '_e4_ba_94', '_e5_85_ad', '_e4_b8_83', '_e5_85_ab', '_e4_b9_9d', '_e5_8d_81', '_e4_b9_9d', '_e5_85_ab', '_e4_b8_83', '_e5_85_ad', '_e4_ba_94', '_e5_9b_9b', '_e4_b8_89', '_e4_ba_8c', '_e4_b8_80', '_e4_ba_8c', '_e4_b8_89', '_e5_9b_9b', '_e4_ba_94', '_e5_85_ad', '_e4_b8_83', '_e5_85_ab', '_e4_b9_9d', '_e5_8d_81'],500,"word_data/","gif.gif")
