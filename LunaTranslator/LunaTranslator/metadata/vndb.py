import requests, re, os
from myutils.config import tryreadconfig, safesave
import gzip, json
import shutil

from metadata.abstract import common


def safegetvndbjson(proxy, url, json, getter):
    try:
        print(url, json)
        _ = requests.post(
            url,
            json=json,
            proxies=proxy,
        )
        print(_.text)
        try:
            return getter(_.json())
        except:
            # print_exc()
            return None
    except:
        return None


def gettitlebyid(proxy, vid):
    def _getter(js):

        try:

            for _ in js["results"][0]["titles"]:
                main = _["main"]
                title = _["title"]
                if main:
                    return title

            raise Exception()
        except:
            return js["results"][0]["title"]

    return safegetvndbjson(
        proxy,
        "https://api.vndb.org/kana/vn",
        {"filters": ["id", "=", vid], "fields": "title,titles.title,titles.main"},
        _getter,
    )


def getscreenshotsbyid(proxy, vid):
    def _getter(js):

        ___ = []
        for _ in js["results"][0]["screenshots"]:
            url = _["url"]
            ___.append(url)
        return ___

    return safegetvndbjson(
        proxy,
        "https://api.vndb.org/kana/vn",
        {"filters": ["id", "=", vid], "fields": "screenshots.url"},
        _getter,
    )


def getimgbyid(proxy, vid):
    return safegetvndbjson(
        proxy,
        "https://api.vndb.org/kana/vn",
        {"filters": ["id", "=", vid], "fields": "image.url"},
        lambda js: js["results"][0]["image"]["url"],
    )


def getvidbytitle_vn(proxy, title):
    return safegetvndbjson(
        proxy,
        "https://api.vndb.org/kana/vn",
        {"filters": ["search", "=", title], "fields": "id", "sort": "searchrank"},
        lambda js: js["results"][0]["id"],
    )


def getvidbytitle_release(proxy, title):
    return safegetvndbjson(
        proxy,
        "https://api.vndb.org/kana/release",
        {
            "filters": ["search", "=", title],
            "fields": "id,vns.id",
            "sort": "searchrank",
        },
        lambda js: js["results"][0]["vns"][0]["id"],
    )


def getdevelopersbyid(proxy, vid):

    def _js(js):
        _ = []
        for item in js["results"][0]["developers"]:
            if item["original"]:
                _.append(item["original"])
            _.append(item["name"])
        return _

    name = safegetvndbjson(
        proxy,
        "https://api.vndb.org/kana/vn",
        {"filters": ["id", "=", vid], "fields": "developers.name,developers.original"},
        _js,
    )
    return name


def getidbytitle_(proxy, title):
    vid = getvidbytitle_vn(proxy, title)
    if vid:
        return vid
    return getvidbytitle_release(proxy, title)


def getcharnamemapbyid(proxy, vid):
    res = safegetvndbjson(
        proxy,
        "https://api.vndb.org/kana/character",
        {
            "filters": [
                "vn",
                "=",
                ["id", "=", vid],
            ],
            "fields": "name,original",
        },
        lambda js: js["results"],
    )
    namemap = {}
    try:
        for r in res:
            namemap[r["original"]] = r["name"]
    except:
        pass
    return namemap


def decompress_gzip_file(gzip_file, output_file):
    with gzip.open(gzip_file, "rb") as f_in:
        with open(output_file, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def safedownload(proxy):
    try:
        resp = requests.get(
            "https://dl.vndb.org/dump/vndb-tags-latest.json.gz",
            proxies=proxy,
        )
        os.makedirs("cache/temp", exist_ok=True)
        with open("cache/temp/vndb-tags-latest.json.gz", "wb") as ff:
            ff.write(resp.content)
        decompress_gzip_file(
            "cache/temp/vndb-tags-latest.json.gz",
            "cache/temp/vndb-tags-latest.json",
        )
        with open("cache/temp/vndb-tags-latest.json", "r", encoding="utf8") as ff:
            js = json.load(ff)
        newjs = {}
        for item in js:
            gid = "g" + str(item["id"])
            name = item["name"]
            newjs[gid] = name
        return newjs
    except:
        from traceback import print_exc

        print_exc()
        return None


def getvntagsbyid(proxy, vid):

    res = safegetvndbjson(
        "https://api.vndb.org/kana/vn",
        {
            "filters": [
                "id",
                "=",
                vid,
            ],
            "fields": "tags.rating",
        },
        lambda js: js["results"][0]["tags"],
    )
    if not res:
        return
    tags = []
    vndbtagdata = tryreadconfig("vndbtagdata.json")
    changed = False
    try:
        for r in res:
            tag = r["id"]
            if tag not in vndbtagdata and not changed:
                js = safedownload(proxy)
                if js:
                    vndbtagdata.update(js)
                changed = True
            if tag not in vndbtagdata:
                continue
            tags.append(vndbtagdata[r["id"]])
    except:
        pass
    if changed:
        safesave("./userconfig/vndbtagdata.json", vndbtagdata)
    return tags



def gettagfromhtml(path):
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf8") as ff:
            html = ff.read()
        find = re.search('<div id="vntags">([\\s\\S]*?)</div>', html)
        if find:
            html = find.groups()[0]
            return [_[1] for _ in re.findall("<a(.*?)>(.*?)</a>", html)]
    return []


class searcher(common):

    def refmainpage(self, _id):
        return f"https://vndb.org/v{_id}"

    def getidbytitle(self, title):
        vid = getidbytitle_(self.proxy, title)
        if vid:
            return int(vid[1:])
        return None

    def searchfordata(self, _vid):
        os.makedirs("./cache/vndb", exist_ok=True)
        vid = "v{}".format(_vid)
        img = getimgbyid(self.proxy, vid)
        title = gettitlebyid(self.proxy, vid)
        namemap = getcharnamemapbyid(self.proxy, vid)
        vndbtags = []  # getvntagsbyid(self.proxy, vid) #这个东西谜之慢
        if len(vndbtags) == 0:
            # 没代理时下不动那个tag的json
            vndbtags = gettagfromhtml(
                self.dispatchdownloadtask(
                    self.refmainpage(_vid), ishtml=True, delay=False
                )
            )
        developers = getdevelopersbyid(self.proxy, vid)
        try:
            imagepath_much2 = [
                self.dispatchdownloadtask(_)
                for _ in getscreenshotsbyid(self.proxy, vid)
            ]
        except:
            imagepath_much2 = []
        _image = self.dispatchdownloadtask(img)
        __ = []
        if _image:
            __.append(_image)
        __ += imagepath_much2
        return {
            "namemap": namemap,
            "title": title,
            "imagepath_all": __,
            "webtags": vndbtags,
            "developers": developers,
        }
