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
    def config(self):
        return self.config_all["args"]

    @property
    def config_all(self):
        try:
            return globalconfig["metadata"][self.typename]
        except:
            return {}

    @property
    def name(self):
        return self.config_all.get("name", self.typename)

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
        def tryremove(pair):
            try:
                globalconfig["metadata"][self.typename]["downloadtasks"].remove(
                    list(pair)
                )
            except:
                pass

        while True:
            pair = self.__tasks.get()
            url, save = pair
            if os.path.exists(save):
                tryremove(pair)
                continue
            if self.__realdodownload(url, save):
                tryremove(pair)
            else:
                self.__tasks.put(pair)
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
            os.makedirs(os.path.dirname(save), exist_ok=True)
            with open(save, "wb") as ff:
                ff.write(_content)
            return True
        except:
            return False

    def dispatchdownloadtask(self, url):
        __routine = f"cache/metadata/{self.typename}"
        if self.typename == "vndb":
            __routine = "cache/vndb"

        if "." in url[5:]:
            __ = url[url.rfind(".") :]
        else:
            __ = ".jpg"
        savepath = f"{__routine}/{self.b64string(url)}{__}"

        globalconfig["metadata"][self.typename]["downloadtasks"].append((url, savepath))
        self.__tasks.put((url, savepath))
        return savepath

    def b64string(self, a):
        return hashlib.md5(a.encode("utf8")).hexdigest()
