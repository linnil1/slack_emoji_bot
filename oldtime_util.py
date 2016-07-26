from bs4 import BeautifulSoup as BS
import urllib.request
import time
import re

def dateTostr(year,month,date):
    if year <= 1900 or year >= 2100:
        raise ValueError("year not good")
    url = "http://www.nongli.info/index.php?c=solar&year="+str(year)+"&month="+str(month)+"&date="+str(date)
    a = urllib.request.urlopen(url).read().decode("utf-8")
    bs = BS(a,"lxml")
    oldmonthday = bs.find("td",attrs={"bgcolor":'#c9f5f7'}).span.text
    oldyear = re.findall(r"\w+",bs.find("font",attrs={"size":4}).text)

    if len(oldyear) == 4 and "臘" not in oldmonthday:#not good condition
        oldyear = oldyear[2:4]
    
    return oldyear[0] + " " + oldyear[1] + " "  + oldmonthday

def minuteTostr(minute):
    if minute >=60 : 
        minute = 59
    old4M = "一二三四"
    nowM =  minute//15
    oldstrM  = old4M  [nowM   ]
    return oldstrM+"刻"

def hourTostr(hour):
    old12H = "子丑寅卯辰巳午未申酉戌亥"
    old2Hs = "初正"
    nowH = (hour+1)%24
    oldstrH  = old12H [nowH//2]
    oldstrHs = old2Hs [nowH% 2]
    return oldstrH+oldstrHs


def timeParse(timestr):
    """
    support format type
    2016/1/2 3:4
    2016/1/2 3:
    2016/1/2
    2016
    3:4
    3:
    :4
    """
    parseformat = ["%Y/%m/%d %H:%M","%Y/%m/%d %H:","%Y/%m/%d","%Y","%H:%M","%H:",":%M"]

    for i in range(len(parseformat)):
        try:
            return time.strptime(timestr,parseformat[i]),i
        except :
            pass

    raise ValueError("not found correct format")

def timeTostr(timestr):
    thetime,timetype = timeParse(timestr.strip())
    if   timetype == 6:
        return minuteTostr(thetime.tm_min)
    elif timetype == 5:
        return hourTostr(thetime.tm_hour)
    elif timetype == 4:
        return hourTostr(thetime.tm_hour) + " " + minuteTostr(thetime.tm_min)
    elif timetype == 3:
        return dateTostr(thetime.tm_year,7,26).split(' ')[0]  # only the year (7/26=Today)
    elif timetype == 2:
        return dateTostr(thetime.tm_year,thetime.tm_mon,thetime.tm_mday)
    elif timetype == 1:
        return dateTostr(thetime.tm_year,thetime.tm_mon,thetime.tm_mday) +(
            "  " + hourTostr(thetime.tm_hour))
    elif timetype == 0:
        return dateTostr(thetime.tm_year,thetime.tm_mon,thetime.tm_mday) +(
            "  " + hourTostr(thetime.tm_hour) + " " + minuteTostr(thetime.tm_min) )

