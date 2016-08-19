from multiprocessing import Pool
import requests
from lxml import html
import re
import random
from urllib.request import urlretrieve


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

def fileUpload(path,name,data):
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
    # if up['Results'] == 2189
    return up['IDBegin']


def gifGet(emojis,delay,path,name):
    #get the date // it is yyyymmddhh 
    rep  = requests.get("http://gifcreator.me/")
    page = html.fromstring(rep.text)
    data = {
       'date' : re.findall("\d+",page.xpath("script")[4].text)[0],
       'folder_name' : randomGet(16) }
    data['folder'] = data['folder_name']
    print(data)
    
    #upload
    indexs = []
    #with Pool(processes=len(emojis)) as pool:
    #   args = [ (path,e,data) for e in emojis ]
    #   indexs  = pool.starmap(fileUpload,args)
    for e in emojis:
        indexs.append(fileUpload(path,e,data))
    print(indexs)

    delays = []
    for i in indexs:
        delays.append("{}_{}_".format(i,delay))
    
    #download
    url = urlGet(data,delays)
    print(url)
    urlretrieve(url,path+name)

#gifGet(['test0','test1','test2','test3','test1','test2','test3','test1','test2','test3','test1','test2','test3'],2000,"word_data/","gif.gif")
