import requests
import random
import re

class NTU118:
    def require():
        return []
    def __init__(self,slack,custom):
        self.slack = slack
        self.req = requests.Session()
        self.req.headers.update({
            'X-CSRFToken': 'tJ6xOJKM41IdEaEcL7lge9uSAw3gRJwD',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent' : 'Mozilla/4.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/40.0',
            'Cookie': 'csrftoken=tJ6xOJKM41IdEaEcL7lge9uSAw3gRJwD'})

    def listGet(self):
        listdata = self.req.post("https://118restaurant.ntu.edu.tw/restaurant/get_list",headers={'Referer': 'https://118restaurant.ntu.edu.tw/home'}).json()['content']
        for i in listdata: # there are some not type QQ
            if not i['food_type']:
                i['food_type'] = "其他"
            i['name'].strip() # name has not stripped
        return listdata
    
    def mainParse(self,store):
        text = "*"+store['name']+"*\n"
        text+= "時間 "+store['opening_hours']+"\n"

        if len(str(store['location'])) > 5:
            gmap = "<http://maps.google.com/maps?q=loc:{},{}&z=20|".format( *reversed(re.findall(r"[0-9.]+",store['location'])) )
            text+= "地點 "+gmap+store['address'] +">\n"
        text+= "電話 "+store['telephone'] +"\n"

        return {'text':text,'attachments':self.attachParse(store['id'])}

    def attachParse(self,id):
        id = str(id)
        att = self.req.post("https://118restaurant.ntu.edu.tw/restaurant/get_info",data={'data':'{"rest_id":'+id+'}'},headers={'Referer': 'https://118restaurant.ntu.edu.tw/detail/'+id}).json()['content']
        arr = []

        #dishes
        if att['dishes'] :
            dishes = {'title':"菜單"}
            dishes['text'] = '\n'.join( [ i['name']+" : "+str(i['price']) for i in att['dishes'] ] )
            arr.append(dishes)

        #comments
        if att['comments'] :
            score = [0]*6
            allscore = 0
            for com in att['comments'] :
                score[ com['score'] ] = score[ com['score'] ] + 1
                allscore = allscore + com['score'] 

            comments = {'title':"評論"}
            comments['text'] = "分數 "+"{:.2}".format(allscore/len(att['comments']))+ "\n"
            comments['text']+= "\n".join( [ "{:★>5} -> {}".format("☆"*(5-i),score[i]) for i in range(5,0,-1)] ) + "\n"
            comments['text']+= "\n".join( [ i['content'] for i in att['comments'] if i['content'] ] )

            arr.append(comments)

        return arr

    def listParse(self,l):
        return ", ".join(l) if len(l) else "Not found"

    def typeGet(self,type_name=""):
        l = self.listGet()
        if type_name: # find restaurant of that type 
            return [ i['name'] for i in l if i['food_type']==type_name ]
        # list types
        return list(set([ i['food_type'] for i in l ]))
    
    def foodFind(self,name):
        l = self.listGet()
        match = [ i for i in l if name and i['name'].find(name)>=0 ]
        if len(match) != 1 :
            return {'text':self.listParse([i['name'] for i in match])}
        return self.mainParse(match[0])

    def allList(self): # sorted by type
        dic = {}
        for r in self.listGet():
            if not dic.get(r['food_type']):
                dic[r['food_type']] = []
            dic[r['food_type']].append(r['name'])
        s = ""
        for k, v in dic.items():
            s += "*"+k+"* "
            s += ", ".join(v)+"\n"
        return s+"https://118restaurant.ntu.edu.tw/home"

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        payload = {
            "username": "NTU118 Eater",
            "icon_emoji": ":_e5_b7_b7:",
            "thread_ts":datadict.get("thread_ts")or'',
            "channel": datadict['channel']
        }
        text_input = datadict['text']

        if text_input.startswith("118help"):
            text = """
`118random     ` get a random restaurant
`118type       ` get all type of restaurant
`118type [type]` get all restaurant of that type
`118list       ` get all restaurant in 118
`118find [name]` list all restaurant which match
`118info [name]` get detailed of that restaurant
`118help       ` get help"""
            self.slack.api_call("chat.postMessage",**payload,text=text)

        elif text_input.startswith("118random"):
            textload = self.mainParse( random.choice(self.listGet()) )
            print(textload)
            self.slack.api_call("chat.postMessage",**payload,**textload)

        elif text_input.startswith("118type"):
            data = re.findall(r"(?<=118type).*",text_input,re.DOTALL)[0].strip()
            self.slack.api_call("chat.postMessage",**payload,text=self.listParse(self.typeGet(data)))
        
        elif text_input.startswith("118list"):
            textload = self.allList()
            self.slack.api_call("chat.postMessage",**payload,text=textload)
        
        elif re.search("^118find |^118info ",text_input):
            data = re.search(r"((?<=118find )|(?<=118info )).*",text_input,re.DOTALL).group().strip()
            textload = self.foodFind(data)
            self.slack.api_call("chat.postMessage",**payload,**textload)

# test this for parse text is correct 
#a  = NTU118("","")
#li = a.listGet()
#for i in li:
#    print( a.mainParse(i) )
