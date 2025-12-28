from tts.basettsclass import TTSbase, SpeechParam


class TTS(TTSbase):
    arg_support_pitch = False
    arg_support_speed = False

    def getvoicelist(self):
        headers = {
            "Connection": "Keep-Alive",
            "Accept-Language": "zh-CN,en,*",
            "User-Agent": "Mozilla/5.0",
        }

        params = {
            "type": "27",
            "mobi_app": "pc_bcut",
            "platform": "android",
            "build": "2180020",
        }

        response = self.proxysession.get(
            "https://member.bilibili.com/x/mvp/material/list",
            params=params,
            headers=headers,
        )

        vis, inter = [], []
        for l in response.json()["data"]["list"]:
            for c in l["children"]:
                inter.append(c["voice"])
                vis.append(l["name"] + " " + c["name"])
        return inter, vis

    def speak(self, content, voice, param: SpeechParam):

        headers = {
            "Connection": "Keep-Alive",
            "Accept-Language": "zh-CN,en,*",
            "User-Agent": "Mozilla/5.0",
        }

        json_data = {
            "model_id": "tts_bcut_pc",
            "raw_data": [
                content,
            ],
            "raw_params": {
                "format": "mp3",
                "logid": "b98553e4-09bb-4d77-bb05-529c27674587",
                "method": 0,
                "pitch_rate": 0,  # 实际上没用
                "sample_rate": 24000,
                "speech_rate": 0,  # 实际上没用
                "task_type": 0,
                "voice": voice,
                "voice_engine": "bili",
                "volume": 50,
            },
        }

        response = self.proxysession.post(
            "https://member.bilibili.com/x/material/rubick-interface/sync-task",
            headers=headers,
            json=json_data,
        )
        response = self.proxysession.get(
            response.json()["data"]["result"]["results"][0]["url"],
            headers=headers,
            stream=True,
        )
        return response
