import base64
from ocrengines.baseocrclass import baseocr


class OCR(baseocr):
    def initocr(self):
        self.tokens = {}
        self.check()

    def check(self):
        self.checkempty(["app_id", "app_secret"])
        app_id = self.config["app_id"]
        app_secret = self.config["app_secret"]
        if (app_id, app_secret) not in self.tokens:
            res = self.proxysession.post(
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                headers={"Content-Type": "application/json; charset=utf-8"},
                json={"app_id": app_id, "app_secret": app_secret},
            )
            try:
                token = res.json()["tenant_access_token"]
            except:
                raise Exception(res.json())
            self.tokens[(app_id, app_secret)] = token
        return self.tokens[(app_id, app_secret)]

    def ocr(self, imagebinary):
        token = self.check()
        b64 = base64.b64encode(imagebinary)
        res = self.proxysession.post(
            "https://open.feishu.cn/open-apis/optical_char_recognition/v1/image/basic_recognize",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": "Bearer " + token,
            },
            json={
                "image": str(b64, encoding="utf8"),
            },
        )
        try:
            return res.json()["data"]["text_list"]
        except:
            raise Exception(res.text)
