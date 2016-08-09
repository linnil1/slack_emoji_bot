import re
class oldreact:
    def __init__(self,old,slack):
        self.OLD = old
        self.slack = slack
        self.futurereact = {}
        # {channel:[{count:,arr:[,]},{}]

    def getFileID(self,payload,ts,count): #count <=0
        count = -count+1 # because inclusive
        target = {}
        for i in range(4):
            target =self.slack.api_call("channels.history",
                    channel=payload['channel'],
                    count=count,
                    latest=ts,
                    inclusive=1)
            if float(target['messages'][0]['ts']) >= float(ts):
                break;
            print("Not newest")
            time.sleep(0.25)
            
        if float(target['messages'][0]['ts']) < float(ts):
            print("Not newest")
            raise ValueError("Not found newest")

        target = target['messages'][count-1]

        if 'comment' in target :
            payload['file_comment'] = target['comment']['id']         
        elif 'file' in target :
            payload['file'] = target['file']['id']         
        else:
            payload['timestamp'] = target['ts']


    def getFloor(self,data):
        """ It should be separated by space and the range is [-F,F] in hex """
        strdig = re.search(r"^-?[0-9a-fA-F]\s",data)
        
        try:
            dig = int(strdig.group(),16)
        except(AttributeError,TypeError,ValueError): #nonetype or strange dig
            raise ValueError

        print("Floor = " + str(dig))
        return dig

    def futurereactCount(self,datadict):
        if datadict['type'] == 'message' :
            if 'subtype' not in datadict or datadict['subtype'] not in ["me_message","message_changed","message_deleted"]:
                ch = datadict['channel']
                if ch not in self.futurereact:
                    return 
                if ch in self.futurereact:
                    mails = self.futurereact[ch]
                    for i in range(len(mails)):
                        mails[i]['count'] -= 1
                        if mails[i]['count'] == 0 :
                            print("future Mail")
                            futuredict = dict(datadict)
                            futuredict['text'] = mails[i]['text']
                            futuredict['future'] = True
                            self.OLD.main(futuredict)
                    self.futurereact[ch] = [ mail for mail in mails if mail['count'] != 0 ] 
            elif datadict['subtype']=="message_deleted":
                #if deleted will cause some count error
                #but i don't want to deal it
                return 

    def futurereactAdd(self,payload,text,floors):
        ch = payload['channel'] 
        if ch not in self.futurereact:
            self.futurereact[ch] = []
        self.futurereact[ch].append({"count":floors,"text":text})
        payload['name'] = "_e8_a1_8c" # ok in chinese
        print(self.slack.api_call("reactions.add",**payload))


    def main(self,payload,emoji_str,ts):
        floors = -1
        futuretext = emoji_str
        try: #if has floor option
            floors = self.getFloor(emoji_str)
            futuretext = re.search(r"( .*)",emoji_str,re.DOTALL).group().strip()
            if floors > 0:
                self.getFileID(payload,ts,0)
                self.futurereactAdd(payload,"oldreact 0 "+futuretext,floors)
                return 
        except:
            pass

        self.getFileID(payload,ts,floors)

        return payload,futuretext
