import requests, re
from myutils.utils import simplehtmlparser


from metadata.abstract import common


class searcher(common):
    def getidbytitle(self, title):

        headers = {
            "Referer": "https://www.dlsite.com/maniax/work/=/product_id/RJ01166543.html",
            "Upgrade-Insecure-Requests": "1",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        try:
            response = requests.get(
                "https://www.dlsite.com/pro/fsr/=/language/jp/sex_category[0]/male/keyword/"
                + title,
                headers=headers,
                proxies=self.proxy,
            )

            inner = simplehtmlparser(
                response.text,
                "div",
                '<div id="search_result_list" class="loading_display_open"',
            )
            # print(inner)
            _id = re.search('id="_link_VJ(.*?)"', inner).groups()[0]

            return "VJ" + _id

        except:
            response = requests.get(
                "https://www.dlsite.com/maniax/fsr/=/language/jp/sex_category[0]/male/keyword/"
                + title,
                headers=headers,
                proxies=self.proxy,
            )

            inner = simplehtmlparser(
                response.text,
                "div",
                '<div id="search_result_list" class="loading_display_open"',
            )
            # print(inner)
            _id = re.search('id="_link_RJ(.*?)"', inner).groups()[0]

            return "RJ" + _id

    def refmainpage(self, RJ: str):
        if RJ.startswith("RJ"):
            return "https://www.dlsite.com/maniax/work/=/product_id/{}.html".format(RJ)
        elif RJ.startswith("VJ"):
            return "https://www.dlsite.com/pro/work/=/product_id/{}.html".format(RJ)

    def searchfordata(self, RJ):

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7,ru;q=0.6",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": "https://www.dlsite.com/home/",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }

        response = self.proxysession.get(
            self.refmainpage(RJ),
            headers=headers,
        )

        title = re.search(
            '<h1 itemprop="name" id="work_name">(.*?)</h1>', response.text
        ).groups()[0]
        print(title)
        devp = re.search(
            '<span itemprop="brand" class="maker_name">([\\s\\S]*?)<a ([\\s\\S]*?)>(.*?)</a>([\\s\\S]*?)</span>',
            response.text,
        ).groups()[2]
        print(devp)
        tags = re.search(
            '<div class="main_genre">([\\s\\S]*?)</div>', response.text
        ).groups()[0]

        tags = [_[1] for _ in re.findall('<a href="(.*?)">(.*?)</a>', tags)]
        print(tags)

        inner = simplehtmlparser(
            response.text,
            "div",
            '<div itemprop="description" class="work_parts_container">',
        )

        imags2 = ["https:" + _[0] for _ in re.findall('<img src="(.*?)"(.*?)>', inner)]
        print(imags2)

        inner = simplehtmlparser(response.text, "div", '<div ref="product_slider_data"')

        imags1 = [
            "https:" + _[0] for _ in re.findall('<div data-src="(.*?)"(.*?)>', inner)
        ]
        print(imags1)
        description = simplehtmlparser(
            response.text, "div", '<div itemprop="description"'
        )
        print(description)
        return {
            "title": title,
            "images": imags1 + imags2,
            "webtags": tags,
            "developers": [devp],
            "description": description,
        }
