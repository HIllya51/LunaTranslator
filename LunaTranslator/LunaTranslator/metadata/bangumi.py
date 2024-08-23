import requests
from myutils.config import savehook_new_data
from myutils.utils import initanewitem, gamdidchangedtask
import functools
from qtsymbols import *
from metadata.abstract import common
from gui.usefulwidget import getlineedit
from gui.dialog_savedgame import getreflist, getalistname
from myutils.wrapper import Singleton_close
from gui.dynalang import LPushButton


@Singleton_close
class bgmsettings(QDialog):

    @property
    def headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Authorization": "Bearer " + self._ref.config["access-token"].strip(),
        }

    @property
    def username(self):
        response = requests.get(
            "https://api.bgm.tv/v0/me", headers=self.headers, proxies=self._ref.proxy
        )
        return response.json()["username"]

    def querylist(self):

        params = {
            "subject_type": "4",
            "limit": "30",
            "offset": "0",
        }
        collectresults = []
        response = requests.get(
            f"https://api.bgm.tv/v0/users/{self.username}/collections",
            params=params,
            headers=self.headers,
            proxies=self._ref.proxy,
        )
        for item in response.json()["data"]:
            collectresults.append(
                {"id": item["subject_id"], "name": item["subject"]["name"]}
            )
        return collectresults

    def getalistname_download(self, uid):

        reflist = getreflist(uid)
        collectresults = self.querylist()
        thislistvids = [
            savehook_new_data[gameuid][self._ref.idname] for gameuid in reflist
        ]
        collect = {}
        for gameuid in savehook_new_data:
            vid = savehook_new_data[gameuid][self._ref.idname]
            collect[vid] = gameuid

        for item in collectresults:
            title = item["name"]
            vid = item["id"]
            if vid in thislistvids:
                continue

            if vid in collect:
                gameuid = collect[vid]
            else:
                gameuid = initanewitem(title)
                savehook_new_data[gameuid][self._ref.idname] = vid
                gamdidchangedtask(self._ref.typename, self._ref.idname, gameuid)
            reflist.insert(0, gameuid)

    def getalistname_upload(self, uid):
        reflist = getreflist(uid)
        vids = [item["id"] for item in self.querylist()]

        for gameuid in reflist:
            vid = savehook_new_data[gameuid][self._ref.idname]
            if vid == 0:
                continue
            if vid in vids:
                continue

            requests.post(
                f"https://api.bgm.tv/v0/users/-/collections/{vid}",
                headers=self.headers,
                json={
                    "type": 4,
                    # "rate": 10,
                    # "comment": "string",
                    # "private": True,
                    # "tags": ["string"],
                },
                proxies=self._ref.proxy,
            )

    def singleupload_existsoverride(self, gameuid):
        vid = savehook_new_data[gameuid][self._ref.idname]
        if not vid:
            return
        try:
            requests.post(
                f"https://api.bgm.tv/v0/users/-/collections/{vid}",
                headers=self.headers,
                json={
                    "type": 4,
                    # "rate": 10,
                    # "comment": "string",
                    # "private": True,
                    # "tags": ["string"],
                },
                proxies=self._ref.proxy,
            )
        except:
            pass

    def __getalistname(self, callback, _):
        getalistname(self, callback)

    def __init__(self, parent, _ref: common, gameuid: str) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self._ref = _ref
        self.resize(QSize(800, 10))
        self.setWindowTitle(self._ref.config_all["name"])
        fl = QFormLayout(self)
        fl.addRow("access-token", getlineedit(_ref.config, "access-token"))
        btn = LPushButton("上传游戏")
        btn.clicked.connect(
            functools.partial(self.singleupload_existsoverride, gameuid)
        )
        fl.addRow(btn)
        btn = LPushButton("上传游戏列表")
        btn.clicked.connect(
            functools.partial(self.__getalistname, self.getalistname_upload)
        )
        fl.addRow(btn)
        btn = LPushButton("获取游戏列表")
        btn.clicked.connect(
            functools.partial(self.__getalistname, self.getalistname_download)
        )
        fl.addRow(btn)
        self.show()


class searcher(common):
    def querysettingwindow(self, parent, gameuid):
        bgmsettings(parent, self, gameuid)

    def getidbytitle(self, title):

        headers = {
            "accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }

        params = {
            "type": "4",
            "responseGroup": "small",
        }

        response = self.proxysession.get(
            "https://api.bgm.tv/search/subject/" + title, params=params, headers=headers
        )
        print(response.text)
        try:
            response = response.json()
        except:
            return None
        if len(response["list"]) == 0:
            return None
        return response["list"][0]["id"]

    def refmainpage(self, _id):
        return f"https://bangumi.tv/subject/{_id}"

    def searchfordata(self, sid):

        headers = {
            "accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        if self.config["access-token"].strip() != "":
            headers["Authorization"] = "Bearer " + self.config["access-token"]
        response = self.proxysession.get(
            f"https://api.bgm.tv/v0/subjects/{sid}", headers=headers
        )
        print(response.text)
        try:
            response = response.json()
        except:
            return {}
        try:
            imagepath = self.dispatchdownloadtask(response["images"]["large"])
        except:
            imagepath = []

        vndbtags = [_["name"] for _ in response["tags"]]
        developers = []
        for _ in response["infobox"]:
            if _["key"] in ["游戏开发商", "开发", "发行"]:
                if isinstance(_["value"], str):
                    developers.append(_["value"])
                else:
                    for __ in _["value"]:
                        if isinstance(__, str):
                            developers.append(__)
                        elif isinstance(__, dict):
                            developers.append(__["v"])
        namemaps = {}
        try:
            charas = self.proxysession.get(
                f"https://api.bgm.tv/v0/subjects/{sid}/characters", headers=headers
            ).json()
            for _ in charas:
                namemaps[_["name"]] = _["name"]
        except:
            pass
        return {
            "namemap": namemaps,
            "title": response["name"],
            "imagepath_all": [imagepath],
            "webtags": vndbtags,
            "developers": developers,
        }
