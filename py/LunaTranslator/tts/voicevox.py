import time
import requests, json
from traceback import print_exc
from tts.basettsclass import TTSbase


class TTS(TTSbase):

    def getvoicelist(self):

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.52",
            "sec-ch-ua": '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        response = requests.get(
            "http://127.0.0.1:{}/speakers".format(self.config['Port']),
            headers=headers,
            proxies={"http": None, "https": None},
        ).json()
        print(response)
        vis = []
        idxs = []
        for speaker in response:
            name = speaker["name"]
            styles = speaker["styles"]
            for style in styles:
                idxs.append(style["id"])
                vis.append(name + " " + style["name"])

        return idxs, vis

    def speak(self, content, rate, voice):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        params = {"speaker": voice, "text": content}

        response = requests.post(
            "http://localhost:{}/audio_query".format(self.config['Port']),
            params=params,
            headers=headers,
            proxies={"http": None, "https": None},
        )
        print(response.json())
        headers = {
            "Content-Type": "application/json",
        }
        params = {
            "speaker": voice,
        }
        response = requests.post(
            "http://localhost:{}/synthesis".format(self.config['Port']),
            params=params,
            headers=headers,
            data=json.dumps(response.json()),
        )
        return response.content
