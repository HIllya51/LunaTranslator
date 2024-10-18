from translator.basetranslator import basetrans


class TS(basetrans):

    def translate(self, content):

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.1.5.825 Yowser/2.5 Safari/537.36"
        }
        params = {
            "lang": "{}-{}".format(self.srclang, self.tgtlang),
            "text": content,
        }
        url = "https://browser.translate.yandex.net/api/v1/tr.json/translate"
        params = {**{"srv": "browser_video_translation"}, **params}
        response = self.proxysession.post(
            url=url,
            params=params,
            data={"maxRetryCount": 2, "fetchAbortTimeout": 500},
            headers=headers,
        )

        try:
            return response.json()["text"][0]
        except:
            raise Exception(response.maybejson)
