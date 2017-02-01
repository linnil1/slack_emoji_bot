from imgurpython import ImgurClient
from concurrent.futures import ThreadPoolExecutor

class Imgur:
    def require():
        return [
            {"name": "ImgurId"},
            {"name": "ImgurSecret","secret":True}]

    def __init__(self,privacy):
        self.__client = ImgurClient(privacy['ImgurId' ],privacy['ImgurSecret'])

    def imagesUpload(self,urls):
        """
        for url in urls:
            client.upload_from_url(url)
        """
        if not urls:
            return urls

        with ThreadPoolExecutor(max_workers=16) as executor:
            return list(executor.map(self.imageUpload,urls))

    def imageUpload(self,url):
        try:
            return self.__client.upload_from_url(url)['link']
        except:
            return url

