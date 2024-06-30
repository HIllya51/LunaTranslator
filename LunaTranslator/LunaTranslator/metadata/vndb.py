import requests, re
from myutils.config import savegametaged, _TR, savehook_new_data
from myutils.utils import initanewitem, gamdidchangedtask
import functools
import time
from qtsymbols import *
from gui.inputdialog import autoinitdialog
from metadata.abstract import common
from gui.usefulwidget import getlineedit
from gui.dialog_savedgame import getreflist, getalistname
from myutils.wrapper import Singleton_close


def saferequestvndb(proxy, method, url, json=None, headers=None):
    print(method, url, json)
    resp = requests.request(
        method,
        "https://api.vndb.org/kana/" + url,
        headers=headers,
        json=json,
        proxies=proxy,
    )
    if resp.status_code == 429:
        time.sleep(3)
        print("retry 429")
        return saferequestvndb(proxy, method, url, json, headers)
    elif resp.status_code == 400:
        print(resp.text)
        # 400 搜索失败
    else:
        if method.upper() in ["GET", "POST"]:
            try:
                return resp.json()
            except:
                print(resp.status_code)
                print(resp.text)
                return None


def safegetvndbjson(proxy, url, json):
    return saferequestvndb(proxy, "POST", url, json)


def gettitlefromjs(js):
    try:

        for _ in js["titles"]:
            main = _["main"]
            title = _["title"]
            if main:
                return title

        raise Exception()
    except:
        return js["title"]


def getvidbytitle_vn(proxy, title):
    js = safegetvndbjson(
        proxy,
        "vn",
        {"filters": ["search", "=", title], "fields": "id", "sort": "searchrank"},
    )
    if js:
        return js["results"][0]["id"]


def getvidbytitle_release(proxy, title):
    js = safegetvndbjson(
        proxy,
        "release",
        {
            "filters": ["search", "=", title],
            "fields": "id,vns.id",
            "sort": "searchrank",
        },
    )
    if js:
        return js["results"][0]["vns"][0]["id"]


def getidbytitle_(proxy, title):
    vid = getvidbytitle_vn(proxy, title)
    if vid:
        return vid
    return getvidbytitle_release(proxy, title)


def getinfosbyvid(proxy, vid):
    js = safegetvndbjson(
        proxy,
        "vn",
        {
            "filters": ["id", "=", vid],
            "fields": "title,titles.title,titles.main,screenshots.url,image.url,developers.name,developers.original",
        },
    )
    if js:

        imgs = []
        try:
            for _ in js["results"][0]["screenshots"]:
                url = _["url"]
                imgs.append(url)
        except:
            pass
        dev = []
        for item in js["results"][0]["developers"]:
            if item["original"]:
                dev.append(item["original"])
            dev.append(item["name"])
        return dict(
            title=gettitlefromjs(js["results"][0]),
            imgs=[js["results"][0]["image"]["url"]] + imgs,
            dev=dev,
        )


def getcharnamemapbyid(proxy, vid):
    js = safegetvndbjson(
        proxy,
        "character",
        {
            "filters": [
                "vn",
                "=",
                ["id", "=", vid],
            ],
            "fields": "name,original",
        },
    )
    if js:
        res = js["results"]
    else:
        return {}
    namemap = {}
    try:
        for r in res:
            namemap[r["original"]] = r["name"]
    except:
        pass
    return namemap


@Singleton_close
class vndbsettings(QDialog):

    def getalistname(self, after):
        __d = {"k": 0}

        __vis = []
        __uid = []
        for _ in savegametaged:
            if _ is None:
                __vis.append("GLOBAL")
                __uid.append(None)
            else:
                __vis.append(_["title"])
                __uid.append(_["uid"])
        autoinitdialog(
            self,
            _TR("目标"),
            600,
            [
                {
                    "type": "combo",
                    "name": _TR("目标"),
                    "d": __d,
                    "k": "k",
                    "list": __vis,
                },
                {
                    "type": "okcancel",
                    "callback": functools.partial(after, __d, __uid),
                },
            ],
        )

    @property
    def headers(self):
        return {
            "Authorization": f"Token {self._ref.config['Token']}",
        }

    @property
    def userid(self):
        return saferequestvndb(
            self._ref.proxy, "GET", "authinfo", headers=self.headers
        )["id"]

    def querylist(self, title):

        userid = self.userid
        pagei = 1
        collectresults = []
        while True:
            json_data = {
                "user": userid,
                "fields": (
                    "id, vn.title,vn.titles.title,vn.titles.main" if title else "id"
                ),
                "sort": "vote",
                "results": 100,
                "page": pagei,
            }
            pagei += 1
            response = saferequestvndb(
                self._ref.proxy, "POST", "ulist", json=json_data, headers=self.headers
            )
            collectresults += response["results"]
            if not response["more"]:
                break
        return collectresults

    def getalistname_download(self, uid):
        reflist = getreflist(uid)
        collectresults = self.querylist(True)
        thislistvids = [
            savehook_new_data[gameuid][self._ref.idname] for gameuid in reflist
        ]
        collect = {}
        for gameuid in savehook_new_data:
            vid = savehook_new_data[gameuid][self._ref.idname]
            collect[vid] = gameuid

        for item in collectresults:
            title = gettitlefromjs(item["vn"])
            vid = int(item["id"][1:])
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
        vids = [int(item["id"][1:]) for item in self.querylist(False)]

        for gameuid in reflist:
            vid = savehook_new_data[gameuid][self._ref.idname]
            if vid == 0:
                continue
            if vid in vids:
                continue
            saferequestvndb(
                self._ref.proxy,
                "PATCH",
                f"ulist/v{vid}",
                json={
                    "labels_set": [1],
                },
                headers=self.headers,
            )

    def singleupload_existsoverride(self, gameuid):
        vid = savehook_new_data[gameuid][self._ref.idname]
        if not vid:
            return

        saferequestvndb(
            self._ref.proxy,
            "PATCH",
            f"ulist/v{vid}",
            json={
                "labels_set": [1],
                # "labels_unset": [1],
                # "vote" :100
            },
            headers=self.headers,
        )

    def __getalistname(self, callback, _):
        getalistname(self, callback)

    def __init__(self, parent, _ref: common, gameuid: str) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self._ref = _ref
        self.resize(QSize(800, 10))
        self.setWindowTitle(self._ref.config_all["name"])
        fl = QFormLayout(self)
        fl.addRow("Token", getlineedit(_ref.config, "Token"))
        btn = QPushButton(_TR("上传游戏"))
        btn.clicked.connect(
            functools.partial(self.singleupload_existsoverride, gameuid)
        )
        fl.addRow(btn)
        btn = QPushButton(_TR("上传游戏列表"))
        btn.clicked.connect(
            functools.partial(self.__getalistname, self.getalistname_upload)
        )
        fl.addRow(btn)
        btn = QPushButton(_TR("获取游戏列表"))
        btn.clicked.connect(
            functools.partial(self.__getalistname, self.getalistname_download)
        )
        fl.addRow(btn)
        self.show()


class searcher(common):

    def querysettingwindow(self, parent, gameuid):
        vndbsettings(parent, self, gameuid)

    def refmainpage(self, _id):
        return f"https://vndb.org/v{_id}"

    def getidbytitle(self, title):
        vid = getidbytitle_(self.proxy, title)
        if vid:
            return int(vid[1:])
        return None

    def gettagfromhtml(self, _vid):

        headers = {
            "sec-ch-ua": '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            "Referer": "https://vndb.org/",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42",
            "sec-ch-ua-platform": '"Windows"',
        }

        html = self.proxysession.get(self.refmainpage(_vid), headers=headers).text

        find = re.search('<div id="vntags">([\\s\\S]*?)</div>', html)
        if find:
            html = find.groups()[0]
            return [_[1] for _ in re.findall("<a(.*?)>(.*?)</a>", html)]
        else:
            return []

    def searchfordata(self, _vid):
        vid = "v{}".format(_vid)
        infos = getinfosbyvid(self.proxy, vid)

        title = infos["title"]
        namemap = getcharnamemapbyid(self.proxy, vid)
        vndbtags = self.gettagfromhtml(_vid)
        developers = infos["dev"]

        img = [self.dispatchdownloadtask(_) for _ in infos["imgs"]]

        return {
            "namemap": namemap,
            "title": title,
            "imagepath_all": img,
            "webtags": vndbtags,
            "developers": developers,
        }
