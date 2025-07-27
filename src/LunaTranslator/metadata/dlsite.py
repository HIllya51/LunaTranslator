import requests, re
from myutils.utils import simplehtmlparser


from metadata.abstract import common


class searcher(common):
    def getidbytitle(self, title):

        try:
            response = self.proxysession.get(
                "https://www.dlsite.com/pro/fsr/=/language/jp/sex_category[0]/male/keyword/"
                + title
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
            response = self.proxysession.get(
                "https://www.dlsite.com/maniax/fsr/=/language/jp/sex_category[0]/male/keyword/"
                + title
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

        params = {"workno": RJ}
        response = self.proxysession.get(
            "https://www.dlsite.com/maniax/api/=/product.json", params=params
        )
        response = response.json()[0]

        title = response["work_name"]
        print(title)
        devp = response["maker_name"]
        print(devp)

        tags = [_["name"] for _ in response["genres"]]
        print(tags)

        imags2 = ["https:" + response["image_main"]["url"]]
        print(imags2)

        imags1 = ["https:" + _["url"] for _ in response["image_samples"]]
        print(imags1)
        response = self.proxysession.get(self.refmainpage(RJ))
        description = simplehtmlparser(
            response.text, "div", '<div itemprop="description"'
        )
        description = re.sub(r"(?:\r\n|\n|^)\s*(?=\r\n|\n|$)", "", description)
        description = description.replace("\n", "")
        description = description.replace('href="//', 'href="https://')
        description = description.replace('src="//', 'src="https://')
        return {
            "title": title,
            "images": imags2 + imags1,
            "webtags": tags,
            "developers": [devp],
            "description": description,
        }
