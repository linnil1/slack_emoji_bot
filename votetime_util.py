from datetime import datetime as DT
from dateutil.relativedelta import relativedelta as timeRel
from dateutil.parser import parse as timeParse
import re

def getRel(datastr):
    nowstr = str(datastr).strip()
    resultdic = {}
    while nowstr:
        r = re.match(r"(\d+[YMDhms])",nowstr)
        if not r:
            raise ValueError("find strange charcter "+nowstr[0])
        g = r.group()
        if g[-1] in resultdic:
            raise ValueError("find depulicated "+g)
        resultdic[g[-1]] = int(g[:-1])
        nowstr = nowstr[r.end():].strip()

    convert = {
            'Y':'years' ,'h':'hours'  ,
            'M':'months','m':'minutes',
            'D':'days'  ,'s':'seconds'}

    for sub in convert:
        if sub not in resultdic:
            resultdic[convert[sub]] = 0
        else:
            resultdic[convert[sub]] = resultdic.pop(sub)

    return DT.now() + timeRel(**resultdic)

def strParse(datastr):
    """ support
    2016/7/30
    7/30
    7/30 1:2
    7/30 3 (hour)
    1 (hour)
    1:2
    """
    now  = DT.now()
    datastr = datastr.strip()
    try: 
        tmp = DT.strptime(datastr,"%H")
    except ValueError: pass
    else:
        return timeParse(str(tmp.hour)+":0")
    try: 
        tmp = DT.strptime(datastr,"%m%d %H")
    except ValueError: pass
    else:
        return timeParse("{}/{} {}:0".format(tmp.mon,tmp.day,tmp.hour))

    return timeParse(datastr)

def getAbs(datastr):
    t = strParse(datastr)
    if t < DT.now():
        raise ValueError("the time is passed")
    return t

def getduration(t1,t2):#start end
    r = timeRel(t2,t1)
    return "{}Y {}M {}D {}h {}m {}s".format(
            r.years,r.months,r.days,r.hours,r.minutes,r.seconds)

#for testing
"""
import time
while True:
    a = input()
    r = getAbs(a) 
    print( r.strftime("%Y/%m/%d %H:%M:%S"))
    print( getduration(r,DT.now()))

#"""
