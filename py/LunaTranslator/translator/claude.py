from traceback import print_exc
import json
from translator.basetranslator import basetrans
from myutils.utils import createenglishlangmap, checkv1, urlpathjoin


class TS(basetrans):
    def langmap(self):
        return createenglishlangmap()

    def __init__(self, typename):
        self.context = []
        super().__init__(typename)

    def inittranslator(self):
        self.api_key = None

    def translate(self, query):
        self.checkempty(["API_KEY", "model"])
        query = self._gptlike_createquery(
            query, "use_user_user_prompt", "user_user_prompt"
        )
        system = self._gptlike_createsys("使用自定义promt", "自定义promt")
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
            "X-Api-Key": self.multiapikeycurrent["API_KEY"],
        }

        usingstream = self.config["流式输出"]
        data = dict(
            model=self.config["model"],
            messages=message,
            system=system,
            max_tokens=self.config["max_tokens"],
            temperature=temperature,
            stream=usingstream,
        )
        response = self.proxysession.post(
            urlpathjoin(checkv1(self.config["BASE_URL"].strip()), "messages"),
            headers=headers,
            json=data,
            stream=usingstream,
        )
        if usingstream:
            # https://docs.anthropic.com/claude/reference/messages-streaming
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
                        print_exc()
                        raise Exception(response_data)
                    yield msg

        else:
            # https://docs.anthropic.com/claude/reference/messages_post
            try:
                message = (
                    response.json()["content"][0]["text"].replace("\n\n", "\n").strip()
                )
            except:
                raise Exception(response.maybejson)
            yield message
        self.context.append({"role": "user", "content": query})
        self.context.append({"role": "assistant", "content": message})
