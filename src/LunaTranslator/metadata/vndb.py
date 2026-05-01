import requests, re
import time
from qtsymbols import *
from metadata.abstract import common
from gui.usefulwidget import getsimpleswitch


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


def gettitlefromjs(js, main=True):
    try:

        for _ in js["titles"]:
            _main = _["main"]
            title = _["title"]
            if _main == main:
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
                "fields": "name,original,aliases,sex",
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
            namemap[_o] = {
                "aliases": r["aliases"],
                "name": r["name"],
                "sex": r["sex"][0] if r["sex"] else "",
            }
    except:
        pass
    return namemap


def getinfosbyvid(proxy, vid, main=True):
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
            title=gettitlefromjs(js["results"][0], main=main),
            img=js["results"][0]["image"]["url"] if js["results"][0]["image"] else None,
            sc=imgs,
            dev=dev,
            tags=sorted(tags, key=lambda x: -rates[tags.index(x)]),
            description=js["results"][0]["description"],
        )


class vndbsettings(QFormLayout):

    def __init__(self, layout: QVBoxLayout, _ref: common, gameuid: str) -> None:
        super().__init__(None)
        layout.addLayout(self)
        self.tm = None
        self._ref = _ref
        self.addRow(
            "title - main", getsimpleswitch(_ref.config, "title-main", default=True)
        )


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
        infos = getinfosbyvid(self.proxy, vid, main=self.config.get("title-main", True))
        namemap = getcharnamemapbyid(self.proxy, vid)

        return {
            "namemap": namemap,
            "title": infos["title"],
            "images": [infos["img"]] + self.getreleasecvfromhtml(_vid) + infos["sc"],
            "webtags": infos["tags"],
            "developers": infos["dev"],
            "description": infos["description"],
        }
