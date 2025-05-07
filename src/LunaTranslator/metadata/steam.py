import requests, re
from myutils.utils import simplehtmlparser
from metadata.abstract import common
from qtsymbols import *


class searcher(common):

    def getidbytitle(self, title):
        response = requests.get(
            "https://steamcommunity.com/actions/SearchApps/" + title,
            proxies=self.proxy,
        )
        return response.json()[0]["appid"]

    def refmainpage(self, _id):
        return "https://store.steampowered.com/app/{}/_/".format(_id)

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
            "https://store.steampowered.com/api/appdetails?appids={}".format(_id),
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
            "title": data["name"],
            "images": [re.sub("\\?t=(\\d+)", "", _) for _ in images],
            "webtags": tagsofficial,
            "developers": devs,
            "description": data["detailed_description"],
        }
