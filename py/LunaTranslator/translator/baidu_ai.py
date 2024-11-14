from translator.basetranslator import basetrans
import time, json


class TS(basetrans):
    def inittranslator(self):

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "If-Modified-Since": "Mon, 04 Mar 2024 09:40:16 GMT",
            "If-None-Match": '"65e59700-e9b"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        self.proxysession.get(
            "https://fanyi.baidu.com/mtpe-individual/multimodal#/", headers=headers
        )

    def langmap(self):
        return {
            "es": "spa",
            "ko": "kor",
            "fr": "fra",
            "ja": "jp",
            "cht": "cht",
            "vi": "vie",
            "uk": "ukr",
            "ar": "ara",
            "sv": "swe",
            "la": "lat",
        }

    def detectlang(self, query):

        headers = {
            "sec-ch-ua-platform": '"Windows"',
            "Referer": "https://fanyi.baidu.com/mtpe-individual/multimodal",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
        }

        data = {
            "query": query,
        }

        response = self.proxysession.post(
            "https://fanyi.baidu.com/langdetect", headers=headers, data=data
        )
        try:
            return response.json()["lan"]
        except:
            raise Exception(response.maybejson)

    def translate(self, query):

        headers = {
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "accept": "text/event-stream",
            #'Acs-Token':
            "Referer": "https://fanyi.baidu.com/mtpe-individual/multimodal",
            "sec-ch-ua-platform": '"Windows"',
        }

        json_data = {
            "query": query,
            "from": self.detectlang(query) if self.srclang == "auto" else self.srclang,
            "to": self.tgtlang,
            "reference": "",
            "corpusIds": [],
            "qcSettings": [
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "11",
            ],
            "domain": "common",
            "milliTimestamp": int(time.time() * 1000),
        }

        response = self.proxysession.post(
            "https://fanyi.baidu.com/ait/text/translate",
            headers=headers,
            json=json_data,
            stream=True,
        )

        for text in response.iter_lines():
            # print(text,text[:5]!=b'data:',text[:5],b'data:')
            if len(text) == 0 or text[:5] != b"data:":
                continue
            js = json.loads(text[5:].decode("utf8"))
            if js["data"] is None:
                continue
            event = js["data"]["event"]
            if event == "Translating":
                trans = "\n".join([_["dst"] for _ in js["data"]["list"]])
                yield trans
