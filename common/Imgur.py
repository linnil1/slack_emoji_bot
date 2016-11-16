from imgurpython import ImgurClient
from multiprocessing import Pool

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

        pool = Pool(len(urls))
        return pool.map(self.imageUpload,urls)

    def imageUpload(self,url):
        try:
            return self.__client.upload_from_url(url)['link']
        except:
            return url

