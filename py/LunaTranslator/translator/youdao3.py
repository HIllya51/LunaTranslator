from translator.basetranslator import basetrans
import re


class TS(basetrans):
    def langmap(self):
        return {
            "zh": "ZH_CN",
            "ja": "JA",
            "en": "EN",
            "ko": "KR",
            "es": "SP",
            "ru": "RU",
        }

    def inittranslator(self):
        self.proxysession.get(
            "https://m.youdao.com/translate",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Pragma": "no-cache",
                "Referer": "https://www.youdao.com/",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-site",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1",
                "sec-ch-ua": '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
            },
        ).text

    def translate(self, content):
        data = {
            "inputtext": content,
            "type": (
                (self.srclang + "2" + self.tgtlang)
                if self.srclang_1 != "auto"
                else "AUTO"
            ),
        }

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7,ru;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # 'Cookie': 'OUTFOX_SEARCH_USER_ID_NCOO=1687808799.7930427; OUTFOX_SEARCH_USER_ID=883935257@114.94.0.34; UM_distinctid=190bd0ad3d54a1-0822da004c7e09-26001f51-1bcab9-190bd0ad3d6788; _uetsid=b9841280a0d111ef9208815fe9e30d9a; _uetvid=224af48054ce11efa8cdedcb91b3a5c6',
            "Origin": "https://m.youdao.com",
            "Pragma": "no-cache",
            "Referer": "https://m.youdao.com/translate",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        response = self.proxysession.post(
            "https://m.youdao.com/translate",
            data=data,
            headers=headers,
            cookies={
                "OUTFOX_SEARCH_USER_ID_NCOO": "1687808799.7930427",
                "OUTFOX_SEARCH_USER_ID": "883935257@114.94.0.34",
                "UM_distinctid": "190bd0ad3d54a1-0822da004c7e09-26001f51-1bcab9-190bd0ad3d6788",
                "_uetsid": "b9841280a0d111ef9208815fe9e30d9a",
                "_uetvid": "224af48054ce11efa8cdedcb91b3a5c6",
            },
        ).text

        return re.search(
            r'<ul id="translateResult">([\s\S]*?)<li>([\s\S]*?)</li>([\s\S]*?)<\/ul>',
            response,
        ).groups()[1]
