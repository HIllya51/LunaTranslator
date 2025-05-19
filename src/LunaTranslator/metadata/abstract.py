import os, hashlib, queue, gobject, json
from myutils.proxy import getproxy
from threading import Thread
from myutils.commonbase import proxysession
from myutils.config import globalconfig, savehook_new_data, extradatas
from myutils.utils import getlangtgt
from traceback import print_exc
from requests import RequestException
from myutils.wrapper import tryprint


class common:
    typename = None

    def searchfordata(_id) -> "dict[str,str]":
        return None

    def refmainpage(_id) -> str:
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
            info = "{}: {} ".format(self.name, vid)
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
        }

        _content = self.proxysession.get(url, headers=headers).content
        os.makedirs(os.path.dirname(save), exist_ok=True)
        with open(save, "wb") as ff:
            ff.write(_content)

    def dispatchdownloadtask(self, url: str):
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

    def namemapcast(self, namemap: "dict[str,str]"):
        bettermap = namemap.copy()
        for k, v in namemap.items():
            for sp in ["・", " "]:
                spja = k.split(sp)
                spen = v.split(sp if k == v else " ")
                if len(spja) == len(spen) and len(spen) > 1:
                    for i in range(len(spja)):
                        if len(spja[i]) >= 2:
                            bettermap[spja[i]] = spen[i]
        return bettermap

    @tryprint
    def __tryinserttomemory(self, description, gameuid):
        rwpath = gobject.getuserconfigdir("memory/{}".format(gameuid))
        os.makedirs(rwpath, exist_ok=True)

        try:
            with open(os.path.join(rwpath, "config.json"), "r", encoding="utf8") as ff:
                config = json.load(ff)
        except:
            config = []
        filename = None
        for _ in config:
            if _.get("fromweb") == self.typename:
                filename = _.get("file")
        if not filename:
            filename = self.typename + ".md"
            config.append(
                {"file": filename, "title": self.name, "fromweb": self.typename, "edit": False}
            )
            with open(os.path.join(rwpath, "config.json"), "w", encoding="utf8") as ff:
                json.dump(config, ff)
        with open(
            os.path.join(rwpath, self.typename + ".md"), "w", encoding="utf8"
        ) as ff:
            ff.write(description)

    def __do_searchfordata(self, gameuid, vid: str):

        data: "dict[str,str]" = self.searchfordata(vid)
        title = data.get("title", None)
        namemap = data.get("namemap", None)
        developers = data.get("developers", [])
        webtags = data.get("webtags", [])
        images = data.get("images", [])
        description = data.get("description", None)
        if description:
            self.__tryinserttomemory(description, gameuid)
        self.typename
        for _ in images:
            if not _:
                continue
            extradatas["localedpath"][_] = self.dispatchdownloadtask(_)
            extradatas["imagefrom"][_] = self.typename
            if _ in savehook_new_data[gameuid].get("imagepath_all", []):
                continue
            if "imagepath_all" not in savehook_new_data[gameuid]:
                savehook_new_data[gameuid]["imagepath_all"] = []
            savehook_new_data[gameuid]["imagepath_all"].append(_)
        if title:
            if not savehook_new_data[gameuid].get("istitlesetted", False):
                savehook_new_data[gameuid]["title"] = title
        if namemap:
            dedump = set()
            for _ in savehook_new_data[gameuid].get("namemap2", []):
                dedump.add(_.get("key", ""))
            namemap = self.namemapcast(namemap)
            usenamemap = getlangtgt() == "en"
            for name in namemap:
                if name in dedump:
                    continue
                if "namemap2" not in savehook_new_data[gameuid]:
                    savehook_new_data[gameuid]["namemap2"] = []
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
