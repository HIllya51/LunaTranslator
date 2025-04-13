from translator.basetranslator import basetrans
import json, requests, hmac, hashlib, re
from datetime import datetime, timezone
from myutils.utils import (
    createurl,
    common_list_models,
    common_parse_normal_response,
    markdown_to_html,
)
from myutils.proxy import getproxy
from language import Languages


def list_models(typename, regist):
    return common_list_models(
        getproxy(("fanyi", typename)),
        regist["API接口地址"](),
        regist.get("SECRET_KEY", lambda: "")().split("|")[0],
    )


def stream_event_parser(response: requests.Response):

    for response_data in response.iter_lines(decode_unicode=True):
        response_data = response_data.strip()
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


def commonparseresponse_good(
    response: requests.Response, hidethinking: bool, markdown2html: bool
):
    message = ""
    thinkcnt = 0
    isthinking = False
    isreasoning_content = False
    unsafethinkonce = True
    for json_data in stream_event_parser(response):
        try:
            if len(json_data["choices"]) == 0:
                continue
            delta = json_data["choices"][0].get("delta", {})
            msg: str = delta.get("content", None)
            reasoning_content: str = delta.get("reasoning_content", None)
            if reasoning_content:
                if hidethinking:
                    isreasoning_content = True
                    thinkcnt += len(reasoning_content)
                    yield "\0"
                    yield "thinking {} ...".format(thinkcnt)
                else:
                    yield reasoning_content
            elif msg:
                if isreasoning_content:
                    isreasoning_content = False
                    yield "\0"
                if hidethinking and (msg.strip() == "<think>"):
                    yield "thinking ..."
                    isthinking = True
                elif hidethinking and isthinking:
                    if msg.strip() == "</think>":
                        isthinking = False
                        yield "\0"
                    else:
                        thinkcnt += len(msg)
                        yield "\0"
                        yield "thinking {} ...".format(thinkcnt)

                else:
                    # 有时，会没有<think>只有</think>比如使用prefill的时候。移除第一个</think>之前的内容
                    if hidethinking and unsafethinkonce and (msg.strip() == "</think>"):
                        isthinking = False
                        message = ""
                        unsafethinkonce = False
                        yield "\0"
                    elif hidethinking and (not message) and (not msg.strip()):
                        # 跳过</think>后的\n
                        pass
                    else:
                        message += msg
                        if markdown2html:
                            _msg = markdown_to_html(message)
                            yield "\0"
                            yield "LUNASHOWHTML" + _msg
                        else:
                            yield msg
            rs = json_data["choices"][0].get("finish_reason")
            if rs and rs != "null":
                break
        except:
            raise Exception(json_data)
    return message


def parseresponsegemini(response: requests.Response, markdown2html: bool):
    line = ""
    for __x in response.iter_lines(decode_unicode=True):
        __x = __x.strip()
        if not __x.startswith('"text":'):
            continue
        __x = json.loads("{" + __x + "}")["text"]
        line += __x
        if markdown2html:
            _msg = markdown_to_html(line)
            yield "\0"
            yield "LUNASHOWHTML" + _msg
        else:
            yield __x
    return line


def parseresponseclaude(response: requests.Response):
    message = ""
    for response_data in response.iter_lines(decode_unicode=True):
        response_data = response_data.strip()
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


def parsestreamresp(
    apiurl: str, response: requests.Response, hidethinking: bool, markdown2html: bool
):
    if (response.status_code != 200) and (
        not response.headers["Content-Type"].startswith("text/event-stream")
    ):
        # application/json
        # text/html
        raise Exception(response)
    if apiurl.startswith("https://generativelanguage.googleapis.com"):
        respmessage = yield from parseresponsegemini(response, markdown2html)
    elif apiurl.startswith("https://api.anthropic.com/v1/messages"):
        respmessage = yield from parseresponseclaude(response)
    else:
        respmessage = yield from commonparseresponse_good(
            response, hidethinking, markdown2html
        )
    return respmessage


class qianfanIAM:

    @staticmethod
    def sign(access_key_id: str, secret_access_key: str):
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
    def getkey(ak: str, sk: str, proxy):
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


def createheaders(apiurl: str, config: dict, maybeuse: dict, proxy):
    _ = {}
    curkey = config["SECRET_KEY"]
    if curkey:
        # 部分白嫖接口可以不填，填了反而报错
        _.update({"Authorization": "Bearer " + curkey})
    if "openai.azure.com/openai/deployments/" in apiurl:
        _.update({"api-key": curkey})
    elif ("qianfan.baidubce.com/v2" in apiurl) and (":" in curkey):
        if not maybeuse.get(curkey):
            Access_Key, Secret_Key = curkey.split(":")
            key = qianfanIAM.getkey(Access_Key, Secret_Key, proxy)
            maybeuse[curkey] = key
        _.update({"Authorization": "Bearer " + maybeuse[curkey]})
    return _


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

    def createdata(self, message, extra):
        temperature = self.config["Temperature"]
        data = dict(
            model=self.config["model"],
            messages=message,
            # optional
            max_tokens=self.config["max_tokens"],
            # n=1,
            # stop=None,
            top_p=self.config["top_p"],
            temperature=temperature,
            stream=self.config["流式输出"],
        )
        if self.config.get("frequency_penalty_use", False):
            data.update(dict(frequency_penalty=self.config["frequency_penalty"]))
        data.update(extra)
        return data

    def createheaders(self, extra):
        headers = createheaders(
            self.apiurl, self.multiapikeycurrent, self.maybeuse, self.proxy
        )
        if "luna_headers" in extra:
            hh = extra.pop("luna_headers")
            headers.update(hh)
        return headers

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
            try:
                extra = {}
                if self.config["use_other_args"]:
                    try:
                        extra = json.loads(self.config["other_args"])
                    except:
                        extra = eval(self.config["other_args"])
            except:
                pass
            response = self.proxysession.post(
                self.createurl(),
                headers=self.createheaders(extra),
                json=self.createdata(message, extra),
                stream=usingstream,
            )
        hidethinking = self.config.get("hidethinking", False)
        markdown2html = self.config.get("markdown2html", False)
        if usingstream:
            respmessage = yield from parsestreamresp(
                self.apiurl, response, hidethinking, markdown2html
            )
        else:
            respmessage = common_parse_normal_response(
                response, self.apiurl, hidethinking=hidethinking
            )
            if markdown2html:
                yield "LUNASHOWHTML" + markdown_to_html(respmessage)
            else:
                yield respmessage
        if not (query.strip() and respmessage.strip()):
            return
        self.context.append({"role": "user", "content": query})
        self.context.append({"role": "assistant", "content": respmessage})

    def createurl(self):
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
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_CIVIC_INTEGRITY",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]
        }
        # https://discuss.ai.google.dev/t/gemma-3-missing-features-despite-announcement/71692/13
        sys_message = (
            {"systemInstruction": {"parts": {"text": sysprompt}}} if sysprompt else {}
        )
        message = []
        self._gpt_common_parse_context(
            message, self.context, self.config["附带上下文个数"], isgemini=True
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
