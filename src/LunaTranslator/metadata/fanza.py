import re
from myutils.utils import simplehtmlparser


from metadata.abstract import common


class searcher(common):
    def getidbytitle(self, title):
        cookies = {
            "top_pv_uid": "764317a4-3d99-46be-8f5a-6e6762b6059d",
            "top_dummy": "d1776405-0683-4936-824a-d48d2660ccd2",
            "guest_id": "DRNHXB5TDV9XVA__",
            "ckcy": "1",
            "mbox": "check#true#1717923986|session#1717923925784-847103#1717925786",
            "is_intarnal": "true",
            "__utma": "125690133.86996065.1717923926.1717923926.1717923926.1",
            "__utmb": "125690133.0.10.1717923926",
            "__utmc": "125690133",
            "__utmz": "125690133.1717923926.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
            "_gcl_au": "1.1.745157082.1717923927",
            "rieSh3Ee_ga": "GA1.1.1543544133.1717923927",
            "AMP_TOKEN": "%24NOT_FOUND",
            "_dga": "GA1.3.86996065.1717923926",
            "_dga_gid": "GA1.3.1715736403.1717923928",
            "_dc_gtm_UA-48257133-2": "1",
            "i3_ab": "93b99577-b74d-4fef-bba7-7ba426cf40ae",
            "age_check_done": "1",
            "dlsoft_check_item_history": "WyJuYXZlbF8wMDEzQDAiXQ%3D%3D",
            "cklg": "ja",
            "_yjsu_yjad": "1717923940.9d45754c-50f7-4219-8b50-e541815f4906",
            "_dga": "GA1.4.86996065.1717923926",
            "_dga_gid": "GA1.4.1715736403.1717923928",
            "__rtbh.uid": "%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22unknown%22%7D",
            "rieSh3Ee_ga_KQYE0DE5JW": "GS1.1.1717923926.1.1.1717923942.0.0.405570256",
            "cto_bundle": "yi6GA19QYzZmZHhXT0tWaFZZN2o4Y2NBb0lFSUFiWCUyQmJ3OWlTZ05VaWtEeXpoR201SnEyYnVIU3BqRENGeXJDN1VLUU5GOGxVRCUyRjVBa2dZUGFSc2kzSHNoa1FlUGx5Z2xoTElmTE5uc0l1WXpFclFGV1B0TiUyRldXT2ZaV0lXUEV5a2k4and0c2cxJTJGUDZCMWpNV0Q3bExiQktKZyUzRCUzRA",
            "XSRF-TOKEN": "eyJpdiI6ImIyY21vbVJQZloxOUR3ZmJyaWhRdUE9PSIsInZhbHVlIjoiWTRaZ1VTOUw4UmFidnhvbWJkaU11SjZGRmljeWRiQ0cwODIybXI3T29VVmt2VXpub2dZdnBEUTFtN0pZa1BSeWZUQVhzOGR5UXlhVWxPUm1CN2Rwc3c9PSIsIm1hYyI6IjY5OTQ0ZjRmZjBhMGViZGRlN2VlMTQ2M2U3MDRiYjZlODllZWUyMDNlODg4YjQxOTA3ZmQyZDkzZWFhMjM0NmIiLCJ0YWciOiIifQ%3D%3D",
            "laravel_session": "eyJpdiI6Ik41QzkzTkg1alBGVVVmeUdXOWpQWGc9PSIsInZhbHVlIjoia3lYNzVMOEZ3dm15SFNCb3RlYXNQTU9vZkZCeXBzK3BVOVF2dUY0d1c3QktQczVsU2ZRdTUxdkQ4VlBTcmdjdklQMHV3cFVsRVVcL3BCRGIybTNkVUhRPT0iLCJtYWMiOiJhYjkzMjNhZDg2OWI0ZjkyMTlmNzkzNTExOTlmZTBjNDU3NmJlZWUyYmM5ZTQ5NWI4MjAxZDdmNjZiZDA5NTJjIn0%3D",
            "_dd_s": "logs=0&expire=1717924840754",
        }

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7,ru;q=0.6",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Referer": "https://www.dmm.co.jp/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        response = self.proxysession.get(
            "https://dlsoft.dmm.co.jp/search/?floor=digital_pcgame&searchstr={}&service=pcgame".format(
                title
            ),
            headers=headers,
            cookies=cookies,
        )
        _id = re.search(
            "https://pics.dmm.co.jp/digital/pcgame/(.*?)/", response.text
        ).groups()[0]
        return _id

    def refmainpage(self, _id):
        return "https://dlsoft.dmm.co.jp/detail/{}/".format(_id)

    def searchfordata(self, RJ):
        cookies = {
            "top_pv_uid": "764317a4-3d99-46be-8f5a-6e6762b6059d",
            "top_dummy": "d1776405-0683-4936-824a-d48d2660ccd2",
            "guest_id": "DRNHXB5TDV9XVA__",
            "ckcy": "1",
            "mbox": "check#true#1717923986|session#1717923925784-847103#1717925786",
            "is_intarnal": "true",
            "__utma": "125690133.86996065.1717923926.1717923926.1717923926.1",
            "__utmb": "125690133.0.10.1717923926",
            "__utmc": "125690133",
            "__utmz": "125690133.1717923926.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
            "_gcl_au": "1.1.745157082.1717923927",
            "rieSh3Ee_ga": "GA1.1.1543544133.1717923927",
            "AMP_TOKEN": "%24NOT_FOUND",
            "_dga": "GA1.3.86996065.1717923926",
            "_dga_gid": "GA1.3.1715736403.1717923928",
            "_dc_gtm_UA-48257133-2": "1",
            "i3_ab": "93b99577-b74d-4fef-bba7-7ba426cf40ae",
            "age_check_done": "1",
            "dlsoft_check_item_history": "WyJuYXZlbF8wMDEzQDAiXQ%3D%3D",
            "cklg": "ja",
            "_yjsu_yjad": "1717923940.9d45754c-50f7-4219-8b50-e541815f4906",
            "_dga": "GA1.4.86996065.1717923926",
            "_dga_gid": "GA1.4.1715736403.1717923928",
            "__rtbh.uid": "%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22unknown%22%7D",
            "rieSh3Ee_ga_KQYE0DE5JW": "GS1.1.1717923926.1.1.1717923942.0.0.405570256",
            "cto_bundle": "yi6GA19QYzZmZHhXT0tWaFZZN2o4Y2NBb0lFSUFiWCUyQmJ3OWlTZ05VaWtEeXpoR201SnEyYnVIU3BqRENGeXJDN1VLUU5GOGxVRCUyRjVBa2dZUGFSc2kzSHNoa1FlUGx5Z2xoTElmTE5uc0l1WXpFclFGV1B0TiUyRldXT2ZaV0lXUEV5a2k4and0c2cxJTJGUDZCMWpNV0Q3bExiQktKZyUzRCUzRA",
            "XSRF-TOKEN": "eyJpdiI6ImIyY21vbVJQZloxOUR3ZmJyaWhRdUE9PSIsInZhbHVlIjoiWTRaZ1VTOUw4UmFidnhvbWJkaU11SjZGRmljeWRiQ0cwODIybXI3T29VVmt2VXpub2dZdnBEUTFtN0pZa1BSeWZUQVhzOGR5UXlhVWxPUm1CN2Rwc3c9PSIsIm1hYyI6IjY5OTQ0ZjRmZjBhMGViZGRlN2VlMTQ2M2U3MDRiYjZlODllZWUyMDNlODg4YjQxOTA3ZmQyZDkzZWFhMjM0NmIiLCJ0YWciOiIifQ%3D%3D",
            "laravel_session": "eyJpdiI6Ik41QzkzTkg1alBGVVVmeUdXOWpQWGc9PSIsInZhbHVlIjoia3lYNzVMOEZ3dm15SFNCb3RlYXNQTU9vZkZCeXBzK3BVOVF2dUY0d1c3QktQczVsU2ZRdTUxdkQ4VlBTcmdjdklQMHV3cFVsRVVcL3BCRGIybTNkVUhRPT0iLCJtYWMiOiJhYjkzMjNhZDg2OWI0ZjkyMTlmNzkzNTExOTlmZTBjNDU3NmJlZWUyYmM5ZTQ5NWI4MjAxZDdmNjZiZDA5NTJjIn0%3D",
            "_dd_s": "logs=0&expire=1717924840754",
        }

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7,ru;q=0.6",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Referer": "https://www.dmm.co.jp/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        print(self.refmainpage(RJ))
        response = self.proxysession.get(
            self.refmainpage(RJ), headers=headers, cookies=cookies
        )

        title = re.search(
            '<h1 class="productTitle__headline"(.*?)>(.*?)</h1>', response.text
        ).groups()[1]
        print(title)
        devp = re.findall(
            "<li>([\\s\\S]*?)</li>",
            response.text,
        )[2]
        print(devp)
        devp = (
            re.search("<a (.*?)>([\\s\\S]*?)</a>", devp)
            .groups()[1]
            .replace("\n", "")
            .strip()
        )
        print(devp)

        __text = response.text
        tags = []
        while True:
            if __text.find('<tr class="contentsDetailBottom__tableRow">') == -1:
                break
            __text = __text[
                __text.find('<tr class="contentsDetailBottom__tableRow">') :
            ]
            tags = simplehtmlparser(
                __text,
                "tr",
                '<tr class="contentsDetailBottom__tableRow">',
            )
            __text = __text[1:]
            if "ジャンル" not in tags:
                continue
            tags = re.findall(">(.*?)</a>", tags)
            break

        inner = simplehtmlparser(
            response.text,
            "div",
            '<div class="main-area-left">',
        )

        imags2 = [_[0] for _ in re.findall('<img src="(.*?)"(.*?)>', inner)]
        print(imags2)

        inner = simplehtmlparser(response.text, "div", '<div ref="product_slider_data"')

        description = simplehtmlparser(
            response.text, "div", '<div class="area-detail-read">'
        )
        return {
            "title": title,
            "images": [_.replace("js-", "jp-") for _ in imags2],
            "webtags": tags,
            "developers": [devp],
            "description": description,
        }
