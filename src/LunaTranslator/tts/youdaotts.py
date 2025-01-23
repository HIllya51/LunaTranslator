from tts.basettsclass import TTSbase


class TTS(TTSbase):
    def getvoicelist(self):
        return ["ja", "zh", "en"], ["Japanese", "Chinese", "English"]

    def speak(self, content, voice, _):

        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Connection": "keep-alive",
            "Range": "bytes=0-",
            "Referer": "https://fanyi.youdao.com/",
            "Sec-Fetch-Dest": "audio",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42",
            "sec-ch-ua": '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        params = {
            "audio": content,
            "le": voice,
        }

        response = self.proxysession.get(
            "https://dict.youdao.com/dictvoice",
            params=params,
            headers=headers,
        ).content
        return response
