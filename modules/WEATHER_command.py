from selenium import webdriver
import time

class WEATHER: 
    def require():
        return [{"name":"Imgur","module":True}]
    def __init__(self,slack,custom):
        self.slack = slack
        self.imgur = custom['Imgur']
        self.colorPrint = custom['colorPrint']
        self.driver = webdriver.PhantomJS(
                executable_path="./common/node_modules/phantomjs/bin/phantomjs")

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        if datadict['text'] == "weather":
            payload = {
                "username": "Weather Brocaster",
                "icon_emoji": ":_e6_b0_a3:",
                "thread_ts":datadict.get("thread_ts") or '',
                "channel": datadict['channel']}
            self.driver.set_window_size(1024, 768) # set the window size that you need 
            self.driver.get('http://weather.ntustudents.org/')
            path = "data/tmp/weather_"+time.strftime("%s")
            self.colorPrint("Store Image",path)
            self.driver.save_screenshot(path)
            text = "<{}|{}>".format(self.imgur.pathUpload(path),
                                    time.strftime("%c"))
            self.slack.api_call("chat.postMessage",**payload,text=text)
