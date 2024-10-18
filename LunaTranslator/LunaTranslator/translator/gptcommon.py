from translator.basetranslator import basetrans
import json, requests
from myutils.utils import createurl, createenglishlangmap, urlpathjoin
from myutils.proxy import getproxy


def list_models(typename, regist):
    resp = requests.get(
        urlpathjoin(
            createurl(regist["API接口地址"]().strip())[: -len("chat/completions")],
            "models",
        ),
        headers={
            "Authorization": "Bearer " + regist["SECRET_KEY"]().split("|")[0].strip()
        },
        proxies=getproxy(("fanyi", typename)),
        timeout=10,
    )
    try:
        return sorted([_["id"] for _ in resp.json()["data"]])
    except:
        raise Exception(resp.maybejson)


class gptcommon(basetrans):
    @property
    def apiurl(self):
        return self.config.get(
            "API接口地址", self.config.get("OPENAI_API_BASE", "")
        ).strip()

    def langmap(self):
        return createenglishlangmap()

    def __init__(self, typename):
        self.context = []
        super().__init__(typename)

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
            stream=self.config["流式输出"],
        )
        if "api.mistral.ai" not in self.apiurl:
            data.update(dict(frequency_penalty=self.config["frequency_penalty"]))
        try:
            if self.config["use_other_args"]:
                extra = json.loads(self.config["other_args"])
                data.update(extra)
        except:
            pass
        return data

    def createheaders(self):
        _ = {}
        if self.multiapikeycurrent["SECRET_KEY"]:
            # 部分白嫖接口可以不填，填了反而报错
            _.update(
                {"Authorization": "Bearer " + self.multiapikeycurrent["SECRET_KEY"]}
            )
        if "openai.azure.com/openai/deployments/" in self.apiurl:
            _.update({"api-key": self.multiapikeycurrent["SECRET_KEY"]})
        return _

    def commonparseresponse(self, query, response: requests.ResponseBase, usingstream):
        if usingstream:
            message = ""
            if not response.headers["Content-Type"].startswith("text/event-stream"):
                # application/json
                # text/html
                raise Exception(response.maybejson)
            for chunk in response.iter_lines():
                response_data: str = chunk.decode("utf-8").strip()
                if not response_data.startswith("data: "):
                    continue
                response_data = response_data[6:]
                if not response_data:
                    continue
                if response_data == "[DONE]":
                    break
                try:
                    json_data = json.loads(response_data)
                    if len(json_data["choices"]) == 0:
                        continue
                    msg = json_data["choices"][0].get("delta", {}).get("content", None)
                    if msg:
                        message += msg
                        yield msg
                    rs = json_data["choices"][0].get("finish_reason")
                    if rs and rs != "null":
                        break
                except:
                    raise Exception(response_data)
        else:
            try:

                message = (
                    response.json()["choices"][0]["message"]["content"]
                    .replace("\n\n", "\n")
                    .strip()
                )
            except:
                raise Exception(response.maybejson)
            yield message
        self.context.append({"role": "user", "content": query})
        self.context.append({"role": "assistant", "content": message})

    def translate(self, query):
        query = self._gptlike_createquery(
            query, "use_user_user_prompt", "user_user_prompt"
        )
        sysprompt = self._gptlike_createsys("使用自定义promt", "自定义promt")
        message = [{"role": "system", "content": sysprompt}]
        self._gpt_common_parse_context(
            message, self.context, self.config["附带上下文个数"]
        )
        message.append({"role": "user", "content": query})
        prefill = self._gptlike_create_prefill("prefill_use", "prefill")
        if prefill:
            message.append({"role": "assistant", "content": prefill})
        usingstream = self.config["流式输出"]
        print(self.createurl())
        response = self.proxysession.post(
            self.createurl(),
            headers=self.createheaders(),
            json=self.createdata(message),
            stream=usingstream,
        )
        return self.commonparseresponse(query, response, usingstream)

    def createurl(self):
        if "openai.azure.com/openai/deployments/" in self.apiurl:
            return self.apiurl
        return createurl(self.apiurl)
