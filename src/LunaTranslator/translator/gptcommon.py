from translator.basetranslator import basetrans
import json, requests, hmac, hashlib
from datetime import datetime, timezone
from myutils.utils import createurl, common_list_models, common_parse_normal_response
from myutils.proxy import getproxy
from language import Languages


def list_models(typename, regist):
    return common_list_models(
        getproxy(("fanyi", typename)),
        regist["API接口地址"](),
        regist["SECRET_KEY"]().split("|")[0],
    )


def stream_event_parser(response: requests.Response):

    if (response.status_code != 200) and (
        not response.headers["Content-Type"].startswith("text/event-stream")
    ):
        # application/json
        # text/html
        # 谷歌死妈了，流式返回429报错
        raise Exception(response)
    for chunk in response.iter_lines():
        response_data: str = chunk.decode("utf-8").strip()
        if not response_data:
            continue
        if not response_data.startswith("data: "):
            continue
        response_data = response_data[6:]
        if response_data == "[DONE]":
            break
        try:
            json_data = json.loads(response_data)
        except:
            raise Exception(response_data)
        yield json_data


def commonparseresponse_good(response: requests.Response):

    message = ""
    for json_data in stream_event_parser(response):
        try:
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
            raise Exception(json_data)
    return message


def parseresponsecohere(response: requests.Response):
    message = ""
    for json_data in stream_event_parser(response):
        try:
            delta = json_data.get("delta")
            if not delta:
                continue
            if "message" not in delta:
                continue
            content = delta["message"]["content"]
            if not content:
                continue
            msg = content["text"]
        except:
            raise Exception(json_data)
        yield msg
        message += msg
    return message


def parseresponsegemini(response: requests.Response):
    line = ""
    for __x in response.iter_lines(decode_unicode=True):
        __x = __x.strip()
        if not __x.startswith('"text":'):
            continue
        __x = json.loads("{" + __x + "}")["text"]
        yield __x
        line += __x
    return line


def parseresponseclaude(response: requests.Response):
    message = ""
    for chunk in response.iter_lines():
        response_data = chunk.decode("utf-8").strip()
        if not response_data:
            continue
        if response_data.startswith("data: "):
            try:
                json_data = json.loads(response_data[6:])
                if json_data["type"] == "message_stop":
                    break
                elif json_data["type"] == "content_block_delta":
                    msg = json_data["delta"]["text"]
                    message += msg
                elif json_data["type"] == "content_block_start":
                    msg = json_data["content_block"]["text"]
                    message += msg
                else:
                    continue
            except:
                raise Exception(response_data)
            yield msg
    return message


def parsestreamresp(apiurl: str, response: requests.Response):
    if apiurl.startswith("https://generativelanguage.googleapis.com"):
        respmessage = yield from parseresponsegemini(response)
    elif apiurl.startswith("https://api.anthropic.com/v1/messages"):
        respmessage = yield from parseresponseclaude(response)
    elif apiurl.startswith("https://api.cohere.com/v2/chat"):
        respmessage = yield from parseresponsecohere(response)
    else:
        respmessage = yield from commonparseresponse_good(response)
    return respmessage


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
    def apiurl(self) -> str:
        return self.config.get(
            "API接口地址", self.config.get("OPENAI_API_BASE", "")
        ).strip()

    def langmap(self):
        return Languages.createenglishlangmap()

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

    def commonparseresponse_good(self, response: requests.Response):

        message = ""
        for json_data in self.stream_event_parser(response):
            try:
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
                raise Exception(json_data)
        return message

    def translate(self, query):
        query = self._gptlike_createquery(
            query, "use_user_user_prompt", "user_user_prompt"
        )
        sysprompt = self._gptlike_createsys("使用自定义promt", "自定义promt")
        usingstream = self.config["流式输出"]
        if self.apiurl.startswith("https://generativelanguage.googleapis.com"):
            response = self.request_gemini(sysprompt, query)
        elif self.apiurl.startswith("https://api.anthropic.com/v1/messages"):
            response = self.req_claude(sysprompt, query)
        else:
            message = [{"role": "system", "content": sysprompt}]
            self._gpt_common_parse_context(
                message, self.context, self.config["附带上下文个数"]
            )
            message.append({"role": "user", "content": query})
            prefill = self._gptlike_create_prefill("prefill_use", "prefill")
            if prefill:
                message.append({"role": "assistant", "content": prefill})
            response = self.proxysession.post(
                self.createurl(),
                headers=self.createheaders(),
                json=self.createdata(message),
                stream=usingstream,
            )
        if usingstream:
            respmessage = yield from parsestreamresp(self.apiurl, response)
        else:
            respmessage = common_parse_normal_response(response, self.apiurl)
            yield respmessage
        self.context.append({"role": "user", "content": query})
        self.context.append({"role": "assistant", "content": respmessage})

    def createurl(self):
        if "openai.azure.com/openai/deployments/" in self.apiurl:
            return self.apiurl
        return createurl(self.apiurl)

    def request_gemini(self, sysprompt, query):
        gen_config = {
            "generationConfig": {
                "stopSequences": [" \n"],
                "temperature": self.config["Temperature"],
            }
        }
        model = self.config["model"]
        safety = {
            "safety_settings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]
        }
        sys_message = {"systemInstruction": {"parts": {"text": sysprompt}}}
        message = []
        self._gpt_common_parse_context(
            message, self.context, self.config["附带上下文个数"]
        )

        message.append({"role": "user", "parts": [{"text": query}]})
        prefill = self._gptlike_create_prefill("prefill_use", "prefill")
        if prefill:
            message.append({"role": "model", "parts": [{"text": prefill}]})
        contents = dict(contents=message)
        usingstream = self.config["流式输出"]
        payload = {}
        payload.update(contents)
        payload.update(safety)
        payload.update(sys_message)
        payload.update(gen_config)
        res = self.proxysession.post(
            "https://generativelanguage.googleapis.com/v1beta/models/{}:{}".format(
                model, ["generateContent", "streamGenerateContent"][usingstream]
            ),
            params={"key": self.multiapikeycurrent["SECRET_KEY"]},
            json=payload,
            stream=usingstream,
        )
        return res

    def req_claude(self, sysprompt, query):
        temperature = self.config["Temperature"]

        message = []
        self._gpt_common_parse_context(
            message, self.context, self.config["附带上下文个数"]
        )
        message.append({"role": "user", "content": query})
        prefill = self._gptlike_create_prefill("prefill_use", "prefill")
        if prefill:
            message.append({"role": "assistant", "content": prefill})
        headers = {
            "anthropic-version": "2023-06-01",
            "accept": "application/json",
            "content-type": "application/json",
            "X-Api-Key": self.multiapikeycurrent["SECRET_KEY"],
        }

        usingstream = self.config["流式输出"]
        data = dict(
            model=self.config["model"],
            messages=message,
            system=sysprompt,
            max_tokens=self.config["max_tokens"],
            temperature=temperature,
            stream=usingstream,
        )
        response = self.proxysession.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            stream=usingstream,
        )
        return response
