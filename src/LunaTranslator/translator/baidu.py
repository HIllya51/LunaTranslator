from language import Languages
from translator.basetranslator import basetrans
import time, json
from traceback import print_exc


class TS(basetrans):
    def langmap(self):
        return {
            Languages.Spanish: "spa",
            Languages.Korean: "kor",
            Languages.French: "fra",
            Languages.Japanese: "jp",
            Languages.Vietnamese: "vie",
            Languages.Ukrainian: "ukr",
            Languages.Arabic: "ara",
            Languages.Swedish: "swe",
            Languages.Latin: "lat",
        }

    def init(self):
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
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        u = "https://fanyi.baidu.com"
        _ = self.proxysession.get(u, headers=headers)
        _ = self.proxysession.get(u, headers=headers)
        self.proxysession.get(
            "https://fanyi.baidu.com/mtpe-individual/multimodal#/", headers=headers
        )
        # 这俩速度基本一样，结果也完全一样
        self.use = [self.translate_v1, self.translate_v2]

    def translate_v1(self, query):
        form_data = {
            "from": self.srclang,
            "to": self.tgtlang,
            "query": query,
            "source": "txt",
        }
        u = "https://fanyi.baidu.com/transapi"
        r = self.proxysession.post(u, data=form_data)
        try:
            return "\n".join([item["dst"] for item in r.json()["data"]])
        except:
            raise Exception(r)

    def detectlang(self, query):

        headers = {
            "sec-ch-ua-platform": '"Windows"',
            "Referer": "https://fanyi.baidu.com/mtpe-individual/multimodal",
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
            raise Exception(response)

    def translate_v2(self, query):

        headers = {
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "accept": "text/event-stream",
            #'Acs-Token':
            "Referer": "https://fanyi.baidu.com/mtpe-individual/multimodal",
            "sec-ch-ua-platform": '"Windows"',
        }

        json_data = {
            "query": query,
            "from": self.detectlang(query) if self.is_src_auto else self.srclang,
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
        )
        for text in response.text.splitlines():
            # print(text,text[:5]!=b'data:',text[:5],b'data:')
            if len(text) == 0 or text[:5] != "data:":
                continue
            js = json.loads(text[5:])
            if js["data"] is None:
                continue
            event = js["data"]["event"]
            if event == "Translating":
                trans = "\n".join([_["dst"] for _ in js["data"]["list"]])
                return trans

    def translate(self, query):
        try:
            return self.use[0](query)
        except:
            print_exc()
            self.use = list(reversed(self.use))

        try:
            return self.use[0](query)
        except Exception as e:
            print_exc()
            raise e
