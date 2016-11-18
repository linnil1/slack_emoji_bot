from lxml import html
import requests

class SLACK_LOGIN_ERROR(Exception):
    pass

def logIn(url,email,password):
    session = requests.Session()
    session.headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0)"
    rep = session.get(url)
    htree = html.fromstring(rep.text)
    crumb = htree.xpath("//*[@name='crumb']")[0].value 
    loginData = {
        'crumb': crumb,
        'email': email,
        'password': password,
        'redir': '',
        'remember':'on',
        'signin':'1'
        }
    rep = session.post(url,data=loginData)

    htree = html.fromstring(rep.text)
    error = htree.xpath("//*[@class='alert alert_error']")
    if error:
        raise SLACK_LOGIN_ERROR

    team = htree.xpath("//title")[0].text
    print(team)
    return session.cookies

def getalert(rep):
    htree = html.fromstring(rep.text)
    alert = htree.xpath("//p[contains(@class, 'alert')]")
    return alert[0].text_content().strip()

class Emoji:
    def require():
        return [
            {"name": "slack_name"}, 
            {"name": "slack_email"},
            {"name": "slack_password","secret":True}]

    def __init__(self,privacy):
        baseurl = "https://{}.slack.com".format(privacy['slack_name'])
        self._url  = baseurl + "/customize/emoji"
        self._cookies = logIn(baseurl,privacy['slack_email'],privacy['slack_password'])

    def _session(self):
        session = requests.Session()
        session.cookies = self._cookies
        return session

    def _crumbGet(self,url):
        rep = self._session().get(url)
        htree = html.fromstring(rep.text)
        return htree.xpath("//*[@name='crumb']")[0].value 

    def upload(self,filepath,filename):
        data = {
            'add': 1,
            'crumb': self._crumbGet(self._url),
            'name': filename,
            'mode': 'data',
        }
        files = {'img': open(filepath+filename, 'rb')}
        rep = self._session().post(self._url, data=data, files=files, allow_redirects=True)
        return getalert(rep)

    def list(self):
        rep = self._session().get(self._url)
        htree = html.fromstring(rep.text)
        tdarray = htree.xpath("//*[@class='emoji_row']")
        emojilist= []
        for td in tdarray:
            tds = td.xpath("td")
            name = tds[1].text.strip()[1:-1]
            Type = tds[2].text.strip()
            auth = tds[3].text.strip()
            link = td.xpath("*/span")[0].attrib['data-original']
            emojilist.append({
                    "name":name,
                    "link":link,
                    "type":Type,
                    "author":auth })
        return emojilist

    def setalias(self,name,newname):
        data = {
            'add'  : 1,
            'crumb': self._crumbGet(self._url),
            'name' : newname,
            'mode' : 'alias',
            'alias': name
        }
        rep = self._session().post(self._url, data=data)
        return getalert(rep)
