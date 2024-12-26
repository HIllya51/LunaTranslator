import requests
from myutils.utils import urlpathjoin, createurl
from myutils.proxy import getproxy
from cishu.cishubase import cishubase
from translator.gptcommon import qianfanIAM


def list_models(typename, regist):
    resp = requests.get(
        urlpathjoin(
            createurl(regist["API接口地址"]().strip())[: -len("chat/completions")],
            "models",
        ),
        headers={
            "Authorization": "Bearer " + regist["SECRET_KEY"]().split("|")[0].strip()
        },
        proxies=getproxy(("cishu", typename)),
    )
    try:
        return sorted([_["id"] for _ in resp.json()["data"]])
    except:
        raise Exception(resp)


class chatgptlike(cishubase):
    def init(self):
        self.maybeuse = {}

    @property
    def apiurl(self):
        return self.config.get(
            "API接口地址", self.config.get("OPENAI_API_BASE", "")
        ).strip()

    def createdata(self, message):
        temperature = self.config["Temperature"]
        data = dict(
            model=self.config["model"],
            messages=message,
            # optional
            max_tokens=self.config["max_tokens"],
            n=1,
            # stop=None,
            top_p=self.config["top_p"],
            temperature=temperature,
        )
        if "api.mistral.ai" not in self.apiurl:
            data.update(dict(frequency_penalty=self.config["frequency_penalty"]))
        return data

    def search(self, word):
        query = self._gptlike_createquery(
            word, "use_user_user_prompt", "user_user_prompt"
        )
        sysprompt = self._gptlike_createsys("使用自定义promt", "自定义promt")
        message = [{"role": "system", "content": sysprompt}]
        message.append({"role": "user", "content": query})
        response = self.proxysession.post(
            self.createurl(),
            headers=self.createheaders(),
            json=self.createdata(message),
        )
        return self.markdown_to_html(self.commonparseresponse(response))

    def createheaders(self):
        _ = {}
        curkey = self.config["SECRET_KEY"]
        if curkey:
            # 部分白嫖接口可以不填，填了反而报错
            _.update({"Authorization": "Bearer " + curkey})
        if "openai.azure.com/openai/deployments/" in self.apiurl:
            _.update({"api-key": curkey})
        elif ("qianfan.baidubce.com/v2" in self.apiurl) and (":" in curkey):
            if not self.maybeuse.get(curkey):
                Access_Key, Secret_Key = curkey.split(":")
                key = qianfanIAM.getkey(Access_Key, Secret_Key, self.proxy)
                self.maybeuse[curkey] = key
            _.update({"Authorization": "Bearer " + self.maybeuse[curkey]})
        return _

    def createurl(self):
        if "openai.azure.com/openai/deployments/" in self.apiurl:
            return self.apiurl
        return createurl(self.apiurl)

    def commonparseresponse(self, response: requests.Response):
        try:
            message = (
                response.json()["choices"][0]["message"]["content"]
                .replace("\n\n", "\n")
                .strip()
            )
        except:
            raise Exception(response)
        return message
