from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {"cht": "zh-Hant"}

    def inittranslator(self):
        self.tokens = {}
        self.check()

    def check(self):
        self.checkempty(["app_id", "app_secret"])
        app_id = self.multiapikeycurrent["app_id"]
        app_secret = self.multiapikeycurrent["app_secret"]
        if (app_id, app_secret) not in self.tokens:
            res = self.proxysession.post(
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                headers={"Content-Type": "application/json; charset=utf-8"},
                json={"app_id": app_id, "app_secret": app_secret},
            )
            try:
                token = res.json()["tenant_access_token"]
            except:
                raise Exception(res)
            self.tokens[(app_id, app_secret)] = token
        return self.tokens[(app_id, app_secret)]

    def translate(self, query):

        token = self.check()
        res = self.proxysession.post(
            "https://open.feishu.cn/open-apis/translation/v1/text/translate",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": "Bearer " + token,
            },
            json={
                "source_language": self.srclang,
                "text": query,
                "target_language": self.tgtlang,
                "glossary": [],
            },
        )
        try:
            return res.json()["data"]["text"]
        except:
            raise Exception(res)
