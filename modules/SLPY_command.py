from threading import Timer
import slpy
class SLPY:
    def require():
        return [
            {"name":"sl_interval","default":0.5},
            {"name":"sl_col","default":70},
            {"name":"sl_row","default":23}]
    def __init__(self,slack,custom):
        self.slack = slack
        self.payload = {
            "username": "蒸汽火車 Steam Locomotive",
            "icon_emoji": ":_e8_bb_8a:"
        }
        self.col = int(custom['sl_col'])
        self.row = int(custom['sl_row'])
        self.interval = float(custom['sl_interval'])
        self.run = False
        self.runsl = None

    def messageRun(self):
        try:
            s =  next(self.runsl)
            t = Timer(self.interval, self.messageRun)
            t.start()
            self.slack.api_call("chat.update",**self.payload,text = "```"+s+"```")
        except:
            self.run = False
            self.slack.api_call("chat.update",**self.payload,text = "END")

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        if not datadict['text'].startswith("sl ") or (
               datadict['channel'][0] == 'D' ):
            return 

        if self.run:
            self.slack.api_call("chat.postMessage",
                    **self.payload,channel=datadict['channel'],text="Wait")
            return 
        
        if datadict['text'].find("help") >=0:
            self.slack.api_call("chat.postMessage",
                    **self.payload,channel=datadict['channel'],text="""```
slpy 
  -r random flags
  -d add dance people
  -l add more locomotives 
     (number of l = number of loco)
  -F Fly
  -c 
  -a add people cry for help```""")
            return None

        self.payload['channel'] =  datadict['channel']
        pre = self.slack.api_call("chat.postMessage",**self.payload,text="start")
        self.payload['ts'] = pre['ts']
        self.runsl = slpy.sl(self.col,self.row,datadict['text'][3:])
        self.run = True
        self.messageRun()

