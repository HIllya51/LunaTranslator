import requests, re
from myutils.config import savehook_new_data
from myutils.utils import initanewitem, gamdidchangedtask
import functools
import time
from qtsymbols import *
from metadata.abstract import common
from gui.gamemanager.dialog import getreflist, getalistname
from myutils.wrapper import threader
from gui.usefulwidget import threebuttons


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
                return resp.text


def safegetvndbjson(proxy, url, json=None, headers=None):
    return saferequestvndb(proxy, "POST", url, json, headers)


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


def getcharnamemapbyid(proxy, vid):
    results = 100
    while True:
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
                "results": results,
            },
        )
        if not js["more"]:
            break
        results += 10
    namemap = {}
    try:
        for r in js["results"]:
            _o = r["original"]
            # 英语游戏没有original
            if not _o:
                _o = r["name"]
            namemap[_o] = r["name"]
    except:
        pass
    return namemap


def getinfosbyvid(proxy, vid):
    js = safegetvndbjson(
        proxy,
        "vn",
        {
            "filters": ["id", "=", vid],
            "fields": "tags.rating,tags.name,title,titles.title,titles.main,screenshots.url,image.url,developers.name,developers.original,description",
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
        tags = [_["name"] for _ in js["results"][0]["tags"]]
        rates = [_["rating"] for _ in js["results"][0]["tags"]]

        return dict(
            title=gettitlefromjs(js["results"][0]),
            img=js["results"][0]["image"]["url"] if js["results"][0]["image"] else None,
            sc=imgs,
            dev=dev,
            tags=sorted(tags, key=lambda x: -rates[tags.index(x)]),
            description=js["results"][0]["description"],
        )


class vndbsettings(QFormLayout):

    @property
    def headers(self):
        return {
            "Authorization": "Token " + self._ref.config["Token"],
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
            savehook_new_data[gameuid].get(self._ref.idname, 0) for gameuid in reflist
        ]
        collect = {}
        for gameuid in savehook_new_data:
            vid = savehook_new_data[gameuid].get(self._ref.idname, 0)
            if not vid:
                continue
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
            vid = savehook_new_data[gameuid].get(self._ref.idname, 0)
            if not vid:
                continue
            if vid in vids:
                continue
            saferequestvndb(
                self._ref.proxy,
                "PATCH",
                "ulist/v{}".format(vid),
                json={
                    "labels_set": [1],
                },
                headers=self.headers,
            )

    def singleupload_existsoverride(self, gameuid):
        vid = savehook_new_data[gameuid].get(self._ref.idname, 0)
        if not vid:
            return

        saferequestvndb(
            self._ref.proxy,
            "PATCH",
            "ulist/v{}".format(vid),
            json={
                "labels_set": [1],
                # "labels_unset": [1],
                # "vote" :100
            },
            headers=self.headers,
        )

    showhide = pyqtSignal(bool)

    @threader
    def checkvalid(self, k):
        self.showhide.emit(False)
        self.lbinfo.setText("")
        t = time.time()
        self.tm = t
        if k != self._ref.config["Token"]:
            self._ref.config["Token"] = k
        response = saferequestvndb(
            self._ref.proxy, "GET", "authinfo", headers=self.headers
        )
        if t != self.tm:
            return
        print(response)
        if isinstance(response, dict) and response.get("username"):
            info = "username: " + response.get("username")
            self.showhide.emit(True)
        else:
            info = response
            self.showhide.emit(False)
        self.lbinfo.setText(info)

    def __init__(self, layout: QVBoxLayout, _ref: common, gameuid: str) -> None:
        super().__init__(None)
        layout.addLayout(self)
        self.tm = None
        self._ref = _ref
        vbox = QVBoxLayout()
        s = QLineEdit()
        self.lbinfo = QLabel()
        s.textChanged.connect(self.checkvalid)
        s.setText(_ref.config["Token"])
        ww = QWidget()
        fl2 = QFormLayout(ww)
        fl2.setContentsMargins(0, 0, 0, 0)
        ww.hide()
        self.fl2 = ww
        self.showhide.connect(self.fl2.setVisible)
        self._token = s
        vbox.addWidget(s)
        vbox.addWidget(self.lbinfo)
        self.addRow("Token", vbox)
        btn = threebuttons(["上传游戏", "上传游戏列表", "获取游戏列表"])
        btn.btn1clicked.connect(
            functools.partial(self.singleupload_existsoverride, gameuid)
        )
        btn.btn2clicked.connect(
            functools.partial(
                getalistname, btn, self.getalistname_upload, title="上传游戏列表"
            )
        )
        btn.btn3clicked.connect(
            functools.partial(
                getalistname, btn, self.getalistname_download, title="添加到列表"
            )
        )
        fl2.addRow(btn)
        self.addRow(ww)


class searcher(common):

    def querysettingwindow(self, gameuid, layout):
        vndbsettings(layout, self, gameuid)

    def refmainpage(self, _id):
        return "https://vndb.org/v{}".format(_id)

    def getidbytitle(self, title):
        vid = getidbytitle_(self.proxy, title)
        if vid:
            return int(vid[1:])
        return None

    def getreleasecvfromhtml(self, _vid):

        headers = {
            "sec-ch-ua": '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            "Referer": "https://vndb.org/",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42",
            "sec-ch-ua-platform": '"Windows"',
        }

        html = self.proxysession.get(
            self.refmainpage(_vid) + "/cv", headers=headers
        ).text
        return [
            "https://t.vndb.org/cv/" + _
            for _ in re.findall('"https://t.vndb.org/cv/(.*?)"', html)
        ]

    def searchfordata(self, _vid):
        vid = "v{}".format(_vid)
        infos = getinfosbyvid(self.proxy, vid)
        namemap = getcharnamemapbyid(self.proxy, vid)

        return {
            "namemap": namemap,
            "title": infos["title"],
            "images": [infos["img"]] + self.getreleasecvfromhtml(_vid) + infos["sc"],
            "webtags": infos["tags"],
            "developers": infos["dev"],
            "description": (
                infos["description"].replace("\n", "<br>")
                if infos["description"]
                else None
            ),
        }
