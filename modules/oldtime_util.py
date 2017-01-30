import requests
from lxml import html
import time
import re
colorPrint = {}

def dateList(url):
    htree = html.fromstring(requests.get(url).text)
    table = htree.xpath("//table")[0]
    table_list = []
    for week,d in enumerate(table.xpath("*/td")[7:]):
        if not d.xpath("span"):
            continue
        table_list.append({
            "name" : d.xpath("span//text()")[0],
            "date" : d.xpath("b//text()")[0],
            "color": len(d.xpath("span[@style]")) > 0 ,
            "now"  : d.attrib.get("bgcolor"),
            "week" : week%7 #sunday = 0
        })

    oldyear = re.findall(r'\w+',htree.xpath("//font[@size='4']")[0].text)
    colorPrint("Calendar",(oldyear,table_list))
    
    return oldyear,table_list

def dateTostr(year,month,date):
    if year <= 1900 or year >= 2100:
        raise ValueError("year not good")
    url = "http://www.nongli.info/index.php?c=solar&year="+str(year)+"&month="+str(month)+"&date="+str(date)
    year,month_list = dateList(url)

    #search if the day is after new year
    if len(year) == 4 :
        for i in month_list:
            if i['name'] == '春節':
                if int(i['date']) <= date:
                    year = year[2:]
                break
    #search today
    for i in month_list:
        if i['now']:
            return " ".join([year[0],year[1],i['name']])

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
    2016/1/2 3
    2016/1/2
    2016
    3:4
    3:
    :4
    """
    parseformat = ["%Y/%m/%d %H:%M","%Y/%m/%d %H","%Y/%m/%d","%Y","%H:%M","%H:",":%M"]

    for i in parseformat:
        try:
            return time.strptime(timestr,i),i
        except :
            pass
    raise ValueError("not found correct format")

def timeTostr(timestr):
    thetime,timetype = timeParse(timestr.strip())
    if timetype == '%Y':
        return dateTostr(thetime.tm_year,7,26).split(' ')[0]  # only the year (7/26=Today)
    text = ""
    if '%Y' in timetype:
        text += dateTostr(thetime.tm_year,thetime.tm_mon,thetime.tm_mday) + ' '
    if '%H' in timetype:
        text += hourTostr(thetime.tm_hour) + ' '
    if '%M' in timetype:
        text += minuteTostr(thetime.tm_hour) + ' '
    return text

def setPrint(cp):
    global colorPrint
    colorPrint = cp
