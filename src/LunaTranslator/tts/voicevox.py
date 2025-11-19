from tts.basettsclass import TTSbase, SpeechParam


class TTS(TTSbase):

    def getvoicelist(self):

        response = self.proxysession.get(
            "http://127.0.0.1:{}/speakers".format(self.config["Port"])
        ).json()
        vis = []
        idxs = []
        for speaker in response:
            name = speaker["name"]
            styles = speaker["styles"]
            for style in styles:
                idxs.append(style["id"])
                vis.append(name + " (" + style["name"] + ")")

        return idxs, vis

    def speak(self, content, voice, param: SpeechParam):

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
        )
        try:
            resp: dict = response.json()
            resp.update({"speedScale": rate, "pitchScale": pitch})
            params = {"speaker": voice}
            response = self.proxysession.post(
                "http://localhost:{}/synthesis".format(self.config["Port"]),
                params=params,
                json=resp,
            )
            return response
        except:
            raise Exception(response)
