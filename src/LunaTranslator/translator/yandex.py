from translator.basetranslator import basetrans


class TS(basetrans):
    needzhconv = True

    def translate(self, content):

        if self.is_src_auto:
            params = {
                "srv": "browser_video_translation",
                "text": content,
            }

            response = self.proxysession.get(
                "https://translate.yandex.net/api/v1/tr.json/detect", params=params
            )
            lang = response.json()["lang"]
        else:
            lang = self.srclang
        params = {
            "lang": "{}-{}".format(lang, self.tgtlang),
            "text": content,
            "srv": "browser_video_translation",
        }
        url = "https://browser.translate.yandex.net/api/v1/tr.json/translate"
        response = self.proxysession.post(
            url=url,
            params=params,
            data={"maxRetryCount": 2, "fetchAbortTimeout": 500},
        )

        try:
            return response.json()["text"][0]
        except:
            raise Exception(response)
