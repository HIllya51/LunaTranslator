import requests, re
from myutils.utils import (
    simplehtmlparser,
    simplehtmlparser_all,
    initanewitem,
    gamdidchangedtask,
)
from metadata.abstract import common
from myutils.config import savehook_new_data
import functools
from qtsymbols import *
from gui.usefulwidget import getlineedit
from gui.dialog_savedgame import getreflist, getalistname
from myutils.wrapper import Singleton_close


@Singleton_close
class steamsettings(QDialog):

    def querylist(self):

        cookies = {"steamLoginSecure": self._ref.config["steamLoginSecure"]}
        headers = {
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": '"Windows"',
        }
        pagei = 0
        collect = []
        while True:
            params = {
                "p": pagei,
                "v": "1",
            }
            pagei += 1

            response = requests.get(
                f'https://store.steampowered.com/wishlist/profiles/{self._ref.config["userid"] }/wishlistdata/',
                cookies=cookies,
                params=params,
                headers=headers,
            )
            if len(response.json()) == 0:
                break
            for k, v in response.json().items():
                print(k)
                print(v["name"])
                collect.append([k, v["name"]])
        return collect

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
            vid, title = item
            if vid in thislistvids:
                continue

            if vid in collect:
                gameuid = collect[vid]
            else:
                gameuid = initanewitem(title)
                savehook_new_data[gameuid][self._ref.idname] = vid
                gamdidchangedtask(self._ref.typename, self._ref.idname, gameuid)
            reflist.insert(0, gameuid)

    def __getalistname(self, callback, _):
        getalistname(self, callback)

    def __init__(self, parent, _ref: common, gameuid: str) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self._ref = _ref
        self.resize(QSize(800, 10))
        self.setWindowTitle(self._ref.config_all["name"])
        fl = QFormLayout(self)
        fl.addRow("userid", getlineedit(_ref.config, "userid"))
        fl.addRow(
            "cookie:steamLoginSecure", getlineedit(_ref.config, "steamLoginSecure")
        )

        btn = QPushButton("wishlist")
        btn.clicked.connect(
            functools.partial(self.__getalistname, self.getalistname_download)
        )
        fl.addRow(btn)
        self.show()


class searcher(common):

    def querysettingwindow(self, parent, gameuid):
        steamsettings(parent, self, gameuid)

    def getidbytitle(self, title):

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7,ru;q=0.6",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Referer": "https://store.steampowered.com/app/1638230/_/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        params = {
            "term": title,
        }

        response = requests.get(
            "https://store.steampowered.com/search/",
            params=params,
            headers=headers,
            proxies=self.proxy,
        )

        inner = simplehtmlparser(
            response.text, "div", '<div class="col search_capsule">'
        )
        return int(re.search("steam/apps/(.*?)/", inner).groups()[0])

    def refmainpage(self, _id):
        return f"https://store.steampowered.com/app/{_id}/_/"

    def searchfordata(self, _id):
        print(self.refmainpage(_id))

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7,ru;q=0.6",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        html = requests.get(
            self.refmainpage(_id),
            headers=headers,
            proxies=self.proxy,
            cookies={"steamLoginSecure": self.config["steamLoginSecure"]},
        ).text

        imgsshow = [
            f"https://{_[0]}/store_item_assets/steam/apps/{_id}/{_[1]}"
            for _ in re.findall(
                f'"https://(.*?)/store_item_assets/steam/apps/{_id}/(.*?)"', html
            )
        ]
        __ = []
        for _ in imgsshow:
            if " " in _:
                continue
            _ = re.sub("\\.(\\d+)x(\\d+)", "", _)
            _ = re.sub("\\?t=(\\d+)", "", _)
            if _.lower().endswith(".gif"):
                continue
            __.append(_)
        title = re.search(
            '<div id="appHubAppName" class="apphub_AppName">(.*?)</div>', html
        ).groups()[0]

        inner = simplehtmlparser(
            html,
            "div",
            '<div id="genresAndManufacturer"',
        )

        tags = set(
            [
                _.replace(",", "").strip()
                for _ in re.findall(
                    ">(.*?)<", simplehtmlparser(inner, "span", "<span data-panel=")
                )
            ]
        )

        tagsuser = simplehtmlparser(
            html,
            "div",
            '<div data-panel="{&quot;flow-children&quot;:&quot;row&quot;}" class="glance_tags popular_tags"',
        )

        tagsuser = set(
            [_.replace(",", "").strip() for _ in re.findall(">([\\s\\S]*?)<", tagsuser)]
        )

        tagsall = tagsuser.union(tags)
        for _ in ("", "+"):
            if _ not in tagsall:
                continue
            tagsall.remove(_)

        inners = simplehtmlparser_all(
            html,
            "div",
            '<div class="dev_row">',
        )
        devp = set([re.search("(.*)>(.*?)</a>", __).groups()[1] for __ in inners])
        return {
            # "namemap": namemap,
            "title": title,
            "imagepath_all": [self.dispatchdownloadtask(_) for _ in __],
            "webtags": list(tagsall),
            "developers": list(devp),
        }
