from tts.basettsclass import TTSbase, SpeechParam


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
            "sec-ch-ua": '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        response = self.proxysession.get(
            "http://127.0.0.1:{}/speakers".format(self.config["Port"]),
            headers=headers,
        ).json()
        vis = []
        idxs = []
        for speaker in response:
            name = speaker["name"]
            styles = speaker["styles"]
            for style in styles:
                idxs.append(style["id"])
                vis.append(name + " " + style["name"])

        return idxs, vis

    def speak(self, content, voice, param: SpeechParam):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # 0.5-1-2
        if param.speed > 0:
            rate = 1 + param.speed / 10
        else:
            rate = 1 + param.speed / 20
        # -0.15-0.15
        pitch = 0.015 * param.pitch
        params = {"speaker": voice, "text": content}

        response = self.proxysession.post(
            "http://localhost:{}/audio_query".format(self.config["Port"]),
            params=params,
            headers=headers,
        )
        headers = {
            "Content-Type": "application/json",
        }
        resp = response.json()
        resp.update({"speedScale": rate, "pitchScale": pitch})
        params = {"speaker": voice}
        response = self.proxysession.post(
            "http://localhost:{}/synthesis".format(self.config["Port"]),
            params=params,
            headers=headers,
            json=resp,
        )
        return response
