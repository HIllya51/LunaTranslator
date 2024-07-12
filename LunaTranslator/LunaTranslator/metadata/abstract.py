import os, hashlib, queue, gobject
from myutils.proxy import getproxy
from threading import Thread
from myutils.commonbase import proxysession
from myutils.config import globalconfig, savehook_new_data
from traceback import print_exc
from requests import RequestException


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
    def idname(self):
        return self.config_all["target"]

    @property
    def proxy(self):
        return getproxy(("metadata", self.typename))

    def __init__(self, typename) -> None:
        self.typename = typename
        self.proxysession = proxysession("metadata", self.typename)
        self.__tasks_downloadimg = queue.Queue()
        self.__tasks_searchfordata = queue.Queue()
        for internal in globalconfig["metadata"][self.typename]["downloadtasks"]:
            self.__tasks_downloadimg.put(internal)
        for internal in globalconfig["metadata"][self.typename]["searchfordatatasks"]:
            self.__tasks_searchfordata.put(internal)
        Thread(target=self.__tasks_downloadimg_thread).start()
        Thread(target=self.__tasks_searchfordata_thread).start()

    def __safe_remove_task(self, name, pair):
        try:
            for i in range(len(globalconfig["metadata"][self.typename][name])):
                if all(
                    [
                        pair[j] == globalconfig["metadata"][self.typename][name][i][j]
                        for j in range(len(pair))
                    ]
                ):
                    globalconfig["metadata"][self.typename][name].pop(i)
                    break
        except:
            print_exc()

    def __tasks_searchfordata_thread(self):

        while True:
            pair = self.__tasks_searchfordata.get()
            if len(pair) == 2:
                gameuid, vid = pair
                retrytime = 5
            elif len(pair) == 3:
                gameuid, vid, retrytime = pair
            remove = True
            try:
                self.__do_searchfordata(gameuid, vid)
                vis = f"{self.config_all['name']}: {vid} data loaded success"
            except RequestException:
                remove = False
                vis = f"{self.config_all['name']}: {vid} network error, retry later"
            except:
                print_exc()
                vis = f"{self.config_all['name']}: {vid} load failed"
            if remove:

                self.__safe_remove_task("searchfordatatasks", pair)
            else:
                if retrytime:
                    # 尝试5次仍不行则放弃
                    self.__tasks_searchfordata.put((gameuid, vid, retrytime - 1))
                else:
                    self.__safe_remove_task("searchfordatatasks", pair)
            gobject.baseobject.translation_ui.displayglobaltooltip.emit(vis)

    def __tasks_downloadimg_thread(self):
        while True:
            pair = self.__tasks_downloadimg.get()
            url, save = pair

            remove = True
            try:
                self.__do_download_img(url, save)
            except RequestException:
                remove = False
            except:
                print_exc()
            if remove:
                self.__safe_remove_task("downloadtasks", pair)
            else:
                self.__tasks_downloadimg.put(pair)

    def __do_download_img(self, url, save):
        print(url, save)
        if os.path.exists(save):
            return
        headers = {
            "sec-ch-ua": '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            "Referer": "https://vndb.org/",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42",
            "sec-ch-ua-platform": '"Windows"',
        }

        _content = self.proxysession.get(url, headers=headers).content
        os.makedirs(os.path.dirname(save), exist_ok=True)
        with open(save, "wb") as ff:
            ff.write(_content)

    def dispatchdownloadtask(self, url):
        __routine = f"cache/metadata/{self.typename}"
        if self.typename == "vndb":
            __routine = "cache/vndb"

        if "." in url[5:]:
            __ = url[url.rfind(".") :]
        else:
            __ = ".jpg"
        savepath = f"{__routine}/{self.__b64string(url)}{__}"

        globalconfig["metadata"][self.typename]["downloadtasks"].append((url, savepath))
        self.__tasks_downloadimg.put((url, savepath))
        return savepath

    def __b64string(self, a: str):
        return hashlib.md5(a.encode("utf8")).hexdigest()

    def __do_searchfordata(self, gameuid, vid):

        data = self.searchfordata(vid)
        title = data.get("title", None)
        namemap = data.get("namemap", None)
        developers = data.get("developers", [])
        webtags = data.get("webtags", [])
        imagepath_all = data.get("imagepath_all", [])
        normaled = [
            os.path.normpath(os.path.abspath(_))
            for _ in savehook_new_data[gameuid]["imagepath_all"]
        ]
        for _ in imagepath_all:
            if _ is None:
                continue
            if os.path.normpath(os.path.abspath(_)) not in normaled:
                savehook_new_data[gameuid]["imagepath_all"].append(_)
        if title:
            if not savehook_new_data[gameuid]["istitlesetted"]:
                savehook_new_data[gameuid]["title"] = title
            _vis = globalconfig["metadata"][self.typename]["name"]
            _url = self.refmainpage(vid)
            _urls = [_[1] for _ in savehook_new_data[gameuid]["relationlinks"]]
            if _url not in _urls:
                savehook_new_data[gameuid]["relationlinks"].append((_vis, _url))
        if namemap:
            if (len(savehook_new_data[gameuid]["namemap"]) == 0) or (
                not savehook_new_data[gameuid]["vndbnamemap_modified"]
            ):
                savehook_new_data[gameuid]["namemap"] = namemap
                savehook_new_data[gameuid]["vndbnamemap_modified"] = False
        if len(webtags):
            savehook_new_data[gameuid]["webtags"] = webtags
        if len(developers):
            savehook_new_data[gameuid]["developers"] = developers
        return True

    def dispatchsearchfordata(self, gameuid, vid):
        globalconfig["metadata"][self.typename]["searchfordatatasks"].append(
            (gameuid, vid)
        )
        self.__tasks_searchfordata.put((gameuid, vid))
