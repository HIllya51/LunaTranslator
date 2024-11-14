from translator.basetranslator import basetrans
import json, requests, time, hmac, hashlib
from datetime import datetime, timezone
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
    )
    try:
        return sorted([_["id"] for _ in resp.json()["data"]])
    except:
        raise Exception(resp.maybejson)


class qianfanIAM:

    @staticmethod
    def sign(access_key_id, secret_access_key):
        now = datetime.now(timezone.utc)
        canonical_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        sign_key_info = "bce-auth-v1/{}/{}/8640000".format(
            access_key_id, canonical_time
        )
        sign_key = hmac.new(
            secret_access_key.encode(), sign_key_info.encode(), hashlib.sha256
        ).hexdigest()
        string_to_sign = "GET\n/v1/BCE-BEARER/token\nexpireInSeconds=8640000\nhost:iam.bj.baidubce.com"
        sign_result = hmac.new(
            sign_key.encode(), string_to_sign.encode(), hashlib.sha256
        ).hexdigest()
        return "{}/host/{}".format(sign_key_info, sign_result)

    @staticmethod
    def getkey(ak, sk, proxy):
        headers = {
            "Host": "iam.bj.baidubce.com",
            "Authorization": qianfanIAM.sign(ak, sk),
        }
        return requests.get(
            "https://iam.bj.baidubce.com/v1/BCE-BEARER/token",
            params={"expireInSeconds": 8640000},
            headers=headers,
            proxies=proxy,
        ).json()["token"]


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
        self.maybeuse = {}
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
        curkey = self.multiapikeycurrent["SECRET_KEY"]
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

    def commonparseresponse(self, query, response: requests.ResponseBase, usingstream):
        if usingstream:
            message = ""
            if (
                not response.headers["Content-Type"].startswith("text/event-stream")
            ) and (response.status_code != 200):
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
