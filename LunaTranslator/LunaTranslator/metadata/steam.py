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
        response = requests.get(
            "https://steamcommunity.com/actions/SearchApps/" + title,
            proxies=self.proxy,
        )
        return response.json()[0]["appid"]

    def refmainpage(self, _id):
        return f"https://store.steampowered.com/app/{_id}/_/"

    def gettagfromhtml(self, _id):

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
        ).text
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
        return list(tagsall)

    def searchfordata(self, _id):
        data = requests.get(
            f"https://store.steampowered.com/api/appdetails?appids={_id}",
            proxies=self.proxy,
        ).json()[str(_id)]["data"]

        devs = data.get("developers", []) + data.get("publishers", [])
        tagsofficial = [
            _["description"] for _ in data.get("genres", [])
        ] + self.gettagfromhtml(_id)
        images = (
            [data.get("header_image", None)]
            + [data.get("capsule_image", None)]
            + [_["path_full"] for _ in data.get("screenshots", [])]
            + [data.get("background", None)]
            + [data.get("background_raw", None)]
        )
        return {
            # "namemap": namemap,
            "title": data["name"],
            "imagepath_all": [
                self.dispatchdownloadtask(re.sub("\\?t=(\\d+)", "", _)) for _ in images
            ],
            "webtags": tagsofficial,
            "developers": devs,
        }
