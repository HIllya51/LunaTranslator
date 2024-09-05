from traceback import print_exc
import json, requests
from myutils.utils import createenglishlangmap
from translator.basetranslator import basetrans
from myutils.proxy import getproxy


"""
{'response_id': 'f6299ecb-b90a-4582-84e9-3c5c5c586919', 'text': 'In Chinese characters, "Monday" is written as: 星期一\n\nIs there anything else you would like me to translate for you?', 'generation_id': '998f2d14-1af7-4ec3-8699-b164c67a6900', 'chat_history': [{'role': 'USER', 'message': 'translate it to chinese'}, {'role': 'CHATBOT', 'message': 'ok'}, {'role': 'USER', 'message': 'today is monday'}, {'role': 'CHATBOT', 'message': 'In Chinese characters, "Monday" is written as: 星期一\n\nIs there anything else you would like me to translate for you?'}], 'finish_reason': 'COMPLETE', 'meta': {'api_version': {'version': '1'}, 'billed_units': {'input_tokens': 10, 'output_tokens': 29}, 'tokens': {'input_tokens': 82, 'output_tokens': 29}}}

{"is_finished":false,"event_type":"stream-start","generation_id":"2c3aeaf6-8e34-479e-84ce-a669d01a6e02"}
{"is_finished":false,"event_type":"text-generation","text":"In"}
{"is_finished":false,"event_type":"text-generation","text":" Chinese"}
{"is_finished":false,"event_type":"text-generation","text":","}
{"is_finished":false,"event_type":"text-generation","text":" \""}
{"is_finished":false,"event_type":"text-generation","text":"Monday"}
{"is_finished":false,"event_type":"text-generation","text":"\""}
{"is_finished":false,"event_type":"text-generation","text":" is"}
{"is_finished":false,"event_type":"text-generation","text":" translated"}
{"is_finished":false,"event_type":"text-generation","text":" as"}
{"is_finished":false,"event_type":"text-generation","text":" \""}
{"is_finished":false,"event_type":"text-generation","text":"星期"}
{"is_finished":false,"event_type":"text-generation","text":"一"}
{"is_finished":false,"event_type":"text-generation","text":"\""}
{"is_finished":false,"event_type":"text-generation","text":" ("}
{"is_finished":false,"event_type":"text-generation","text":"X"}
{"is_finished":false,"event_type":"text-generation","text":"īng"}
{"is_finished":false,"event_type":"text-generation","text":"q"}
{"is_finished":false,"event_type":"text-generation","text":"ī"}
{"is_finished":false,"event_type":"text-generation","text":" y"}
{"is_finished":false,"event_type":"text-generation","text":"ī"}
{"is_finished":false,"event_type":"text-generation","text":")."}
{"is_finished":false,"event_type":"text-generation","text":" Have"}
{"is_finished":false,"event_type":"text-generation","text":" a"}
{"is_finished":false,"event_type":"text-generation","text":" great"}
{"is_finished":false,"event_type":"text-generation","text":" Monday"}
{"is_finished":false,"event_type":"text-generation","text":"!"}
{"is_finished":true,"event_type":"stream-end","response":{"response_id":"b7b03042-b877-4f25-bece-59b3ba9f4e2a","text":"In Chinese, \"Monday\" is translated as \"星期一\" (Xīngqī yī). Have a great Monday!","generation_id":"2c3aeaf6-8e34-479e-84ce-a669d01a6e02","chat_history":[{"role":"USER","message":"translate it to chinese"},{"role":"CHATBOT","message":"ok"},{"role":"USER","message":"today is monday"},{"role":"CHATBOT","message":"In Chinese, \"Monday\" is translated as \"星期一\" (Xīngqī yī). Have a great Monday!"}],"finish_reason":"COMPLETE","meta":{"api_version":{"version":"1"},"billed_units":{"input_tokens":10,"output_tokens":26},"tokens":{"input_tokens":82,"output_tokens":26}}},"finish_reason":"COMPLETE"}
"""


class TS(basetrans):
    def langmap(self):
        return createenglishlangmap()

    def __init__(self, typename):
        self.context = []
        super().__init__(typename)

    def inittranslator(self):
        self.api_key = None

    def translate(self, query):
        self.checkempty(["SECRET_KEY", "model"])
        self.contextnum = int(self.config["附带上下文个数"])

        query = self._gptlike_createquery(
            query, "use_user_user_prompt", "user_user_prompt"
        )
        sysprompt = self._gptlike_createsys("使用自定义promt", "自定义promt")
        message = [{"role": "system", "message": sysprompt}]
        temperature = self.config["Temperature"]

        message.append(
            {
                "role": "CHATBOT",
                "message": "ok",
            }
        )
        for _i in range(min(len(self.context) // 2, self.contextnum)):
            i = (
                len(self.context) // 2
                - min(len(self.context) // 2, self.contextnum)
                + _i
            )
            message.append(self.context[i * 2])
            message.append(self.context[i * 2 + 1])

        headers = {"Authorization": "Bearer " + self.multiapikeycurrent["SECRET_KEY"]}
        usingstream = self.config["流式输出"]
        data = dict(
            model=self.config["model"],
            chat_history=message,
            message=query,
            # optional
            max_tokens=2048,
            n=1,
            stop=None,
            top_p=1,
            temperature=temperature,
            stream=usingstream,
        )
        response = self.proxysession.post(
            "https://api.cohere.ai/v1/chat",
            headers=headers,
            json=data,
            stream=usingstream,
        )

        if usingstream:
            message = ""
            for chunk in response.iter_lines():
                response_data = chunk.decode("utf-8").strip()
                if not response_data:
                    continue
                try:
                    json_data = json.loads(response_data)
                    t = json_data["event_type"]
                    if t == "text-generation":
                        msg = json_data["text"]
                        message += msg
                    elif t == "stream-end":
                        break
                    else:
                        continue
                except:
                    print_exc()
                    raise Exception(response_data)
                yield msg

        else:
            try:
                message = response.json()["text"]
            except:
                raise Exception(response.text)
            yield message
        self.context.append({"role": "USER", "message": query})
        self.context.append({"role": "CHATBOT", "message": message})


def list_models(typename, regist):
    js = requests.get(
        "https://api.cohere.com/v1/models",
        headers={
            "Authorization": "Bearer " + regist["SECRET_KEY"]().split("|")[0],
            "X-Client-Name": "my-cool-project",
        },
        proxies=getproxy(("fanyi", typename)),
    ).json()
    try:
        models = js["models"]
    except:
        raise Exception(js)
    mm = []
    for m in models:
        endpoints = m["endpoints"]
        if "chat" not in endpoints:
            continue
        mm.append(m["name"])
    return mm
