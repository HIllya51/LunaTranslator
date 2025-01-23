import os, hashlib, queue, gobject
from myutils.proxy import getproxy
from threading import Thread
from myutils.commonbase import proxysession
from myutils.config import globalconfig, savehook_new_data, namemapcast, extradatas
from myutils.utils import getlangtgt
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
                retrytime = 3
            elif len(pair) == 3:
                gameuid, vid, retrytime = pair
            remove = True
            info = "{}: {} ".format(self.config_all["name"], vid)
            try:
                self.__do_searchfordata(gameuid, vid)
                vis = info + "data loaded success"
            except RequestException:
                remove = False
                vis = info + "network error, retry later"
            except:
                print_exc()
                vis = info + " load failed"
            if remove:

                self.__safe_remove_task("searchfordatatasks", pair[:2])
            else:
                if retrytime:
                    self.__tasks_searchfordata.put((gameuid, vid, retrytime - 1))
                else:
                    self.__safe_remove_task("searchfordatatasks", pair[:2])
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
        if os.path.exists(save):
            return
        print(url, save)
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
        if not url:
            return None
        __routine = "cache/metadata/" + self.typename
        if self.typename == "vndb":
            __routine = "cache/vndb"

        if "." in url[-5:]:
            __ = url[url.rfind(".") :]
        else:
            __ = ".jpg"
        savepath = __routine + "/" + self.__b64string(url) + __

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
        images = data.get("images", [])
        description = data.get("description", None)
        for _ in images:
            if not _:
                continue
            extradatas["localedpath"][_] = self.dispatchdownloadtask(_)
            extradatas["imagefrom"][_] = self.typename
            if _ in savehook_new_data[gameuid]["imagepath_all"]:
                continue
            savehook_new_data[gameuid]["imagepath_all"].append(_)
        if title:
            if not savehook_new_data[gameuid]["istitlesetted"]:
                savehook_new_data[gameuid]["title"] = title
            _vis = globalconfig["metadata"][self.typename]["name"]
            _url = self.refmainpage(vid)
            _urls = [_[1] for _ in savehook_new_data[gameuid]["relationlinks"]]
            if _url not in _urls:
                savehook_new_data[gameuid]["relationlinks"].append((_vis, _url))
        if description and not savehook_new_data[gameuid].get("description"):
            savehook_new_data[gameuid]["description"] = description
        if namemap:
            dedump = set()
            for _ in savehook_new_data[gameuid]["namemap2"]:
                dedump.add(_.get("key", ""))
            namemap = namemapcast(namemap)
            usenamemap = getlangtgt() == "en"
            for name in namemap:
                if name in dedump:
                    continue
                savehook_new_data[gameuid]["namemap2"].append(
                    {
                        "key": name,
                        "value": namemap[name] if usenamemap else name,
                        "regex": False,
                        "escape": False,
                    }
                )

        for _ in webtags:
            if _ in savehook_new_data[gameuid]["webtags"]:
                continue
            savehook_new_data[gameuid]["webtags"].append(_)

        for _ in developers:
            if _ in savehook_new_data[gameuid]["developers"]:
                continue
            savehook_new_data[gameuid]["developers"].append(_)
        return True

    def dispatchsearchfordata(self, gameuid, vid):
        globalconfig["metadata"][self.typename]["searchfordatatasks"].append(
            (gameuid, vid)
        )
        self.__tasks_searchfordata.put((gameuid, vid))
