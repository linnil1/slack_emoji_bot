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
        return self.req.post("https://118restaurant.ntu.edu.tw/restaurant/get_list",headers={'Referer': 'https://118restaurant.ntu.edu.tw/home'}).json()['content']
    
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

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        if datadict['text'].startswith("118random"):
            payload = {
                "username": "NTU118 Eater",
                "icon_emoji": ":_e5_b7_b7:",
                "channel": datadict['channel']
            }
            textload = self.mainParse( random.choice(self.listGet()) )
            print(textload)
            self.slack.api_call("chat.postMessage",**payload,**textload)

# test this for parse text is correct 
#a  = NTU118("","")
#li = a.listGet()
#for i in li:
#    print( a.mainParse(i) )
