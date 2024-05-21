import time, requests, re, os, hashlib
from myutils.proxy import getproxy
from myutils.config import globalconfig, vndbtagdata
from threading import Thread
import gzip, json
import shutil


def b64string(a):
    return hashlib.md5(a.encode("utf8")).hexdigest()


def vndbdownloadimg(url, wait=True):
    os.makedirs("./cache/vndb", exist_ok=True)
    savepath = "./cache/vndb/" + b64string(url) + ".jpg"
    if os.path.exists(savepath):
        return savepath

    def _(url, savepath):
        headers = {
            "sec-ch-ua": '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            "Referer": "https://vndb.org/",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42",
            "sec-ch-ua-platform": '"Windows"',
        }
        try:
            time.sleep(1)
            _content = requests.get(url, headers=headers, proxies=getproxy()).content
            with open(savepath, "wb") as ff:
                ff.write(_content)
            return savepath
        except:
            return None

    if wait:
        return _(url, savepath)
    else:
        Thread(target=_, args=(url, savepath)).start()
        return None


def vndbdowloadinfo(vid):
    cookies = {
        "vndb_samesite": "1",
    }

    headers = {
        "authority": "vndb.org",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "sec-ch-ua": '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42",
    }
    url = "https://vndb.org/" + vid
    os.makedirs("./cache/vndb", exist_ok=True)
    savepath = "./cache/vndb/" + b64string(url) + ".html"
    # print(url,savepath)
    if not os.path.exists(savepath):
        try:
            time.sleep(1)
            response = requests.get(
                url, cookies=cookies, headers=headers, proxies=getproxy()
            )
            with open(savepath, "w", encoding="utf8") as ff:
                ff.write(response.text)
        except:
            return None
    return savepath


def safegetvndbjson(url, json, getter):
    try:
        print(url, json)
        _ = requests.post(
            url,
            json=json,
            proxies=getproxy(),
        )
        print(_.text)
        try:
            return getter(_.json())
        except:
            # print_exc()
            return None
    except:
        return None


def gettitlebyid(vid):
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
        "https://api.vndb.org/kana/vn",
        {"filters": ["id", "=", vid], "fields": "title,titles.title,titles.main"},
        _getter,
    )


def getimgbyid(vid):
    return safegetvndbjson(
        "https://api.vndb.org/kana/vn",
        {"filters": ["id", "=", vid], "fields": "image.url"},
        lambda js: js["results"][0]["image"]["url"],
    )


def getvidbytitle_vn(title):
    return safegetvndbjson(
        "https://api.vndb.org/kana/vn",
        {"filters": ["search", "=", title], "fields": "id", "sort": "searchrank"},
        lambda js: js["results"][0]["id"],
    )


def getvidbytitle_release(title):
    return safegetvndbjson(
        "https://api.vndb.org/kana/release",
        {
            "filters": ["search", "=", title],
            "fields": "id,vns.id",
            "sort": "searchrank",
        },
        lambda js: js["results"][0]["vns"][0]["id"],
    )


def getdevelopersbyid(vid):

    def _js(js):
        _ = []
        for item in js["results"][0]["developers"]:
            if item["original"]:
                _.append(item["original"])
            _.append(item["name"])
        return _

    name = safegetvndbjson(
        "https://api.vndb.org/kana/vn",
        {"filters": ["id", "=", vid], "fields": "developers.name,developers.original"},
        _js,
    )
    return name


def getvidbytitle(title):
    vid = getvidbytitle_vn(title)
    if vid:
        return vid
    return getvidbytitle_release(title)


def getcharnamemapbyid(vid):
    res = safegetvndbjson(
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


def safedownload():
    try:
        resp = requests.get(
            "https://dl.vndb.org/dump/vndb-tags-latest.json.gz",
            proxies=getproxy(),
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


def getvntagsbyid(vid):

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
    try:
        for r in res:
            tag = r["id"]
            if tag not in vndbtagdata:
                js = safedownload()
                if js:
                    vndbtagdata.update(js)

            tags.append(r["id"])
    except:
        pass
    return tags


def searchfordata(vid):

    os.makedirs("./cache/vndb", exist_ok=True)
    vid = "v{}".format(vid)
    img = getimgbyid(vid)
    title = gettitlebyid(vid)
    namemap = getcharnamemapbyid(vid)
    vndbtags = getvntagsbyid(vid)
    developers = getdevelopersbyid(vid)
    return {
        "namemap": namemap,
        "title": title,
        "infopath": vndbdowloadinfo(vid),
        "imagepath": vndbdownloadimg(img),
        "vndbtags": vndbtags,
        "developers": developers,
    }


import re


def parsehtmlmethod(infopath):
    with open(infopath, "r", encoding="utf8") as ff:
        text = ff.read()
    ##隐藏横向滚动
    text = text.replace("<body>", '<body style="overflow-x: hidden;">')
    ##删除header
    text = re.sub("<header>([\\s\\S]*?)</header>", "", text)
    text = re.sub("<footer>([\\s\\S]*?)</footer>", "", text)
    text = re.sub('<article class="vnreleases"([\\s\\S]*?)</article>', "", text)
    text = re.sub('<article class="vnstaff"([\\s\\S]*?)</article>', "", text)
    text = re.sub('<article id="stats"([\\s\\S]*?)</article>', "", text)

    text = re.sub("<nav>([\\s\\S]*?)</nav>", "", text)
    text = re.sub('<p class="itemmsg">([\\s\\S]*?)</p>', "", text)
    text = re.sub('<div id="vntags">([\\s\\S]*?)</div>', "", text)
    text = re.sub('<div id="tagops">([\\s\\S]*?)</div>', "", text)
    resavepath = infopath + "parsed.html"

    if globalconfig["languageuse"] == 0:
        text = re.sub(
            '<a href="(.*?)" lang="ja-Latn" title="(.*?)">(.*?)</a>',
            '<a href="\\1" lang="ja-Latn" title="\\3">\\2</a>',
            text,
        )

    hrefs = re.findall('src="(.*?)" width="(.*?)" height="(.*?)"', text)
    # print(hrefs)
    for href in hrefs:
        if href[0].startswith("https://t.vndb.org/st/"):
            href1 = href[0].replace("https://t.vndb.org/st/", "https://t.vndb.org/sf/")
            localimg = vndbdownloadimg(href1, False)
            if localimg:
                text = text.replace(
                    'src="{}" width="{}" height="{}"'.format(href[0], href[1], href[2]),
                    'src="file://{}" width="512"'.format(
                        os.path.abspath(localimg).replace("\\", "/")
                    ),
                )
                text = text.replace(
                    'href="{}"'.format(href1),
                    'href="file://{}"'.format(
                        os.path.abspath(localimg).replace("\\", "/")
                    ),
                )
        elif href[0].startswith("https://t.vndb.org/cv/"):
            localimg = vndbdownloadimg(href[0], False)
            if localimg:
                text = text.replace(
                    'src="{}"'.format(href[0]),
                    'src="file://{}"'.format(
                        os.path.abspath(localimg).replace("\\", "/")
                    ),
                )

    with open(resavepath, "w", encoding="utf8") as ff:
        ff.write(text)

    return resavepath
