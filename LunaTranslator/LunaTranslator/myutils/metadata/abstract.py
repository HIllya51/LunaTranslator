import time, requests, os, hashlib, re, queue
from myutils.proxy import getproxy
from threading import Thread
from myutils.commonbase import proxysession
from myutils.config import globalconfig


class common:
    typename = None

    def searchfordata(_id):
        return None

    def refmainpage(_id):
        return None

    def getidbytitle(title):
        return None

    @property
    def proxy(self):
        return getproxy(("metadata", self.typename))

    def __init__(self, typename) -> None:
        self.typename = typename
        self.proxysession = proxysession("metadata", self.typename)
        self.__tasks = queue.Queue()
        for url, save in globalconfig["metadata"][self.typename]["downloadtasks"]:
            self.__tasks.put((url, save))
        Thread(target=self.__autodownloadimage).start()

    def __autodownloadimage(self):
        while True:
            url, save = self.__tasks.get()
            if os.path.exists(save):
                continue
            if self.__realdodownload(url, save):
                try:
                    globalconfig["metadata"][self.typename]["downloadtasks"].remove(
                        (url, save)
                    )
                except:
                    pass
            else:
                self.__tasks.put((url, save))
            time.sleep(1)

    def __realdodownload(self, url, save):
        if os.path.exists(save):
            return True
        print(url, save)
        headers = {
            "sec-ch-ua": '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            "Referer": "https://vndb.org/",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42",
            "sec-ch-ua-platform": '"Windows"',
        }
        try:
            _content = self.proxysession.get(url, headers=headers).content
            with open(save, "wb") as ff:
                ff.write(_content)
            return True
        except:
            return False

    def dispatchdownloadtask(self, url, ishtml=False, delay=True):
        __routine = f"cache/metadata/{self.typename}"
        if self.typename == "vndb":
            __routine = "cache/vndb"
        os.makedirs(__routine, exist_ok=True)
        if ishtml:
            __ = ".html"
        else:
            if "." in url[5:]:
                __ = url[url.rfind(".") :]
            else:
                __ = ".jpg"
        savepath = f"{__routine}/{self.b64string(url)}{__}"
        if delay:
            globalconfig["metadata"][self.typename]["downloadtasks"].append(
                (url, savepath)
            )
            self.__tasks.put((url, savepath))
            return savepath
        else:
            if self.__realdodownload(url, savepath):
                return savepath
            else:
                return None

    def b64string(self, a):
        return hashlib.md5(a.encode("utf8")).hexdigest()
