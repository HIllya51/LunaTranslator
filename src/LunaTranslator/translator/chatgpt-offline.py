from translator.basetranslator import basetrans
import json, requests, time, re
from myutils.utils import (
    createurl,
    common_list_models,
    common_parse_normal_response,
    markdown_to_html,
)
from typing import Dict, Any, List
from myutils.proxy import getproxy
from language import Languages

# 定义常量
SOPHNET_BASE_URL = "https://www.sophnet.com/api"
PROJECT_UUID = "Ar79PWUQUAhjJOja2orHs"


# 定义数据模型
class AnonymousTokenResponse:
    def __init__(self, data: Dict[str, Any]):
        self.status = data.get("status")
        self.message = data.get("message")
        result = data.get("result", {})
        self.anonymous_token = result.get("anonymousToken")
        self.expires = result.get("expires")
        self.timestamp = data.get("timestamp")


def get_anonymous_token(client: requests.Session) -> str:

    response = client.get(
        f"{SOPHNET_BASE_URL}/sys/login/anonymous",
        headers={
            "Accept": "application/json",
            "User-Agent": "OpenAI-Proxy/1.0",
        },
    )
    response.raise_for_status()
    data = AnonymousTokenResponse(response.json())
    return data.anonymous_token


class SchemaItem:
    def __init__(self, data: Dict[str, Any]):
        self.name = data.get("name")
        self.display_name = data.get("displayName")
        self.des = data.get("des")
        self.type = data.get("type")
        self.range = data.get("range", [])
        self.default_value = data.get("defaultValue")
        self.required = data.get("required", False)


class SophNetModel:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.service_uuid = data.get("serviceUuid")
        self.project_uuid = data.get("projectUuid")
        self.display_name = data.get("displayName")
        self.model_family = data.get("modelFamily")
        self.available = data.get("available", False)
        self.is_base_model = data.get("isBaseModel", False)
        self.features = data.get("features", {})
        self.supported_stream = data.get("supportedStream", False)
        self.supported_image_inputs = data.get("supportedImageInputs", False)
        self.schema = [SchemaItem(item) for item in data.get("schema", [])]


class ModelsResponse:
    def __init__(self, data):
        self.status = data.get("status")
        self.message = data.get("message")
        self.result = [SophNetModel(item) for item in data.get("result", [])]
        self.timestamp = data.get("timestamp")


def get_models(client: requests.Session, token: str):

    response = client.get(
        f"{SOPHNET_BASE_URL}/public/playground/models",
        params={"projectUuid": PROJECT_UUID},
        headers={
            "Accept": "application/json",
            "User-Agent": "OpenAI-Proxy/1.0",
            "Authorization": f"Bearer anon-{token}",
        },
    )
    response.raise_for_status()
    data = ModelsResponse(response.json())
    return data.result


def transform_models_to_openai_format(models: List[SophNetModel]) -> Dict[str, Any]:
    return {
        "object": "list",
        "data": [
            {
                "id": model.model_family,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "sophnet",
                "permission": [
                    {
                        "id": f"modelperm-{model.id}",
                        "object": "model_permission",
                        "created": int(time.time()),
                        "allow_create_engine": False,
                        "allow_sampling": True,
                        "allow_logprobs": False,
                        "allow_search_indices": False,
                        "allow_view": True,
                        "allow_fine_tuning": False,
                        "organization": "*",
                        "group": None,
                        "is_blocking": False,
                    }
                ],
                "root": model.model_family,
                "parent": None,
            }
            for model in models
        ],
    }


def list_models(typename, regist):
    session = requests.Session()
    token = get_anonymous_token(session)
    models = get_models(session, token)
    return sorted([model.model_family for model in models])


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


def parsestreamresp(
    apiurl: str, response: requests.Response, hidethinking: bool, markdown2html: bool
):
    if (response.status_code != 200) and (
        not response.headers["Content-Type"].startswith("text/event-stream")
    ):
        # application/json
        # text/html
        raise Exception(response)
    respmessage = yield from commonparseresponse_good(
        response, hidethinking, markdown2html
    )
    return respmessage


def createheaders(apiurl: str, config: dict, maybeuse: dict, proxy):
    _ = {}
    curkey = config["SECRET_KEY"]
    if curkey:
        # 部分白嫖接口可以不填，填了反而报错
        _.update({"Authorization": "Bearer " + curkey})

    return _


def transform_non_stream_response(response: requests.Response) -> Dict[str, Any]:
    sophnet_response = response.json()
    return (
        sophnet_response.get("choices", [{}])[0].get("message", {}).get("content", "")
    )


def handle_chat_completions(
    client: requests.Session, token: str, request_body: Dict[str, Any], stream: bool
):
    sophnet_body = {
        "temperature": request_body.get("temperature", 1),
        "top_p": request_body.get("top_p", 1),
        "frequency_penalty": request_body.get("frequency_penalty", 0),
        "presence_penalty": request_body.get("presence_penalty", 0),
        "max_tokens": request_body.get("max_tokens", 2048),
        "webSearchEnable": False,
        "stop": request_body.get("stop", []),
        "stream": str(stream),
        "model_id": request_body.get("model"),
        "messages": request_body.get("messages", []),
    }

    response = client.post(
        f"{SOPHNET_BASE_URL}/open-apis/projects/{PROJECT_UUID}/chat/completions",
        json=sophnet_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer anon-{token}",
            "Accept": "text/event-stream" if stream else "application/json",
        },
        timeout=60.0,
        stream=stream,
    )
    response.raise_for_status()
    return response


class TS(basetrans):
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
        if "api.mistral.ai" not in self.apiurl:
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
        if 1:
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

            token = get_anonymous_token(self.proxysession)
            response = handle_chat_completions(
                self.proxysession, token, self.createdata(message, extra), usingstream
            )

        hidethinking = self.config.get("hidethinking", False)
        markdown2html = self.config.get("markdown2html", False)
        if usingstream:
            respmessage = yield from parsestreamresp(
                self.apiurl, response, hidethinking, markdown2html
            )
        else:
            respmessage = transform_non_stream_response(response)
            if hidethinking:
                # 有时，会没有<think>只有</think>比如使用prefill的时候。移除第一个</think>之前的内容
                respmessage = re.sub(r"([\s\S]*)</think>\n*", "", respmessage)

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
