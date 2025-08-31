from translator.basetranslator import basetrans, GptTextWithDict, GptDict
import requests
import json, zhconv
from myutils.utils import urlpathjoin
from language import Languages
from translator.gptcommon import list_models


class TS(basetrans):
    needzhconv = True

    @property
    def is_version_new(self):
        return self.config["prompt_version"] in [1, 2, 3]

    def __init__(self, typename):
        super().__init__(typename)
        self.context = []

    def get_client(self, api_url):
        if api_url[-4:] == "/v1/":
            api_url = api_url[:-1]
        elif api_url[-3:] == "/v1":
            pass
        elif api_url[-1] == "/":
            api_url += "v1"
        else:
            api_url += "/v1"
        self.api_url = api_url
        # OpenAI
        # self.client = OpenAI(api_key="114514", base_url=api_url)

    def make_gpt_dict_text(self, gpt_dict: GptDict):
        gpt_dict_text_list = []
        for gpt in gpt_dict:
            src = gpt.src

            dst = self.checklangzhconv(self.srclang, gpt.dst)
            info = self.checklangzhconv(self.srclang, gpt.info)

            if info:
                single = "{}->{} #{}".format(src, dst, info)
            else:
                single = "{}->{}".format(src, dst)
            gpt_dict_text_list.append(single)

        gpt_dict_raw_text = "\n".join(gpt_dict_text_list)
        return gpt_dict_raw_text

    def _gpt_common_parse_context_2(
        self, messages: list, context, contextnum, ja=False, native=False
    ):
        msgs: "list[str]" = []
        self._gpt_common_parse_context(msgs, context, contextnum)
        __ja, __zh = [], []
        for i, _ in enumerate(msgs):
            [__zh, __ja][i % 2 == 0].append(_.strip())
        if __ja:
            if ja:
                messages.append(
                    {
                        "role": "user",
                        "content": ("" if native else "将下面的日文文本翻译成中文：")
                        + "\n".join(__ja),
                    }
                )
            messages.append({"role": "assistant", "content": "\n".join(__zh)})

    def make_messages(self, query, gpt_dict: GptDict = None):
        contextnum = (
            self.config["append_context_num"] if self.config["use_context"] else 0
        )
        prompt_version = self.config["prompt_version"]
        if prompt_version == 0:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。",
                }
            ]
            self._gpt_common_parse_context_2(messages, self.context, contextnum)
            messages.append(
                {"role": "user", "content": "将下面的日文文本翻译成中文：" + query}
            )
        elif prompt_version == 1:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个轻小说翻译模型，可以流畅通顺地使用给定的术语表以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，注意不要混淆使役态和被动态的主语和宾语，不要擅自添加原文中没有的代词，也不要擅自增加或减少换行。",
                }
            ]
            self._gpt_common_parse_context_2(messages, self.context, contextnum)
            gpt_dict_raw_text = self.make_gpt_dict_text(gpt_dict)
            content = (
                "根据以下术语表（可以为空）：\n"
                + gpt_dict_raw_text
                + "\n\n"
                + "将下面的日文文本根据上述术语表的对应关系和备注翻译成中文："
                + query
            )
            messages.append({"role": "user", "content": content})
        elif prompt_version == 2:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。",
                }
            ]
            self._gpt_common_parse_context_2(messages, self.context, contextnum, True)
            if gpt_dict:
                content = (
                    "根据以下术语表（可以为空）：\n"
                    + self.make_gpt_dict_text(gpt_dict)
                    + "\n"
                    + "将下面的日文文本根据对应关系和备注翻译成中文："
                    + query
                )
            else:
                content = "将下面的日文文本翻译成中文：" + query
            messages.append({"role": "user", "content": content})
        elif prompt_version == 3:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个视觉小说翻译模型，可以通顺地使用给定的术语表以指定的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，注意不要混淆使役态和被动态的主语和宾语，不要擅自添加原文中没有的特殊符号，也不要擅自增加或减少换行。",
                }
            ]
            __gptdict = self.make_gpt_dict_text(gpt_dict)
            if __gptdict:
                __gptdict += "\n"
            __msg = []
            self._gpt_common_parse_context_2(
                __msg, self.context, contextnum, True, True
            )
            content = (
                (("历史翻译：" + __msg[1]["content"] + "\n") if __msg else "")
                + "参考以下术语表（可为空，格式为src->dst #备注）\n"
                + __gptdict
                + "根据以上术语表的对应关系和备注，结合历史剧情和上下文，将下面的文本从日文翻译成简体中文：\n"
                + query
            )
            messages.append({"role": "user", "content": content})
        print(messages)
        return messages

    def send_request(self, messages, is_test=False, **kwargs):
        extra_query = {
            "do_sample": bool(self.config["do_sample"]),
            "num_beams": int(self.config["num_beams"]),
            "repetition_penalty": float(self.config["repetition_penalty"]),
        }

        # OpenAI
        # output = self.client.chat.completions.create(
        data = dict(
            model=self.config["model"],
            messages=messages,
            temperature=float(self.config["temperature"]),
            top_p=float(self.config["top_p"]),
            max_tokens=1 if is_test else int(self.config["max_new_token"]),
            frequency_penalty=float(
                kwargs.get("frequency_penalty", self.config["frequency_penalty"])
            ),
            seed=-1,
            extra_query=extra_query,
            stream=False,
        )
        try:
            output = self.proxysession.post(
                urlpathjoin(self.api_url, "chat/completions"), json=data
            )

        except requests.RequestException as e:
            raise ValueError("无法连接Sakura API，可能未正确部署Sakura模型")
        try:
            yield output.json()
        except:
            raise Exception(output)

    def send_request_stream(self, messages, is_test=False, **kwargs):
        extra_query = {
            "do_sample": bool(self.config["do_sample"]),
            "num_beams": int(self.config["num_beams"]),
            "repetition_penalty": float(self.config["repetition_penalty"]),
        }

        # OpenAI
        # output = self.client.chat.completions.create(
        data = dict(
            model=self.config["model"],
            messages=messages,
            temperature=float(self.config["temperature"]),
            top_p=float(self.config["top_p"]),
            max_tokens=1 if is_test else int(self.config["max_new_token"]),
            frequency_penalty=float(
                kwargs.get("frequency_penalty", self.config["frequency_penalty"])
            ),
            seed=-1,
            extra_query=extra_query,
            stream=True,
        )
        try:
            output = self.proxysession.post(
                urlpathjoin(self.api_url, "chat/completions"),
                json=data,
                stream=True,
            )
        except requests.RequestException:
            raise ValueError("无法连接Sakura API，可能未正确部署Sakura模型")

        if (not output.headers["Content-Type"].startswith("text/event-stream")) and (
            output.status_code != 200
        ):
            raise Exception(output)
        for chunk in output.iter_lines():
            response_data: str = chunk.decode("utf-8").strip()
            if not response_data.startswith("data: "):
                continue
            response_data = response_data[6:]
            if not response_data:
                continue
            if response_data == "[DONE]":
                break
            try:
                res = json.loads(response_data)
            except:
                raise Exception(response_data)

            yield res

    def translate(self, query: GptTextWithDict):

        gpt_dict = query.dictionary
        query: str = query.rawtext if self.is_version_new else query.parsedtext

        self.checkempty(["API接口地址"])
        self.get_client(self.config["API接口地址"])
        frequency_penalty = float(self.config["frequency_penalty"])

        messages = self.make_messages(query, gpt_dict=gpt_dict)
        if bool(self.config["流式输出"]) == True:
            output = self.send_request_stream(messages)
            completion_tokens = 0
            output_text = ""
            for o in output:
                if o["choices"] and (not o["choices"][0]["finish_reason"]):
                    text_partial = o["choices"][0]["delta"].get("content")
                    if not text_partial:
                        continue
                    output_text += text_partial
                    yield text_partial
                    completion_tokens += 1
        else:
            output = self.send_request(messages)
            for o in output:
                completion_tokens = o["usage"]["completion_tokens"]
                output_text = o["choices"][0]["message"]["content"]
                yield output_text

        if bool(self.config["fix_degeneration"]):
            cnt = 0
            # print(completion_tokens)
            while completion_tokens == int(self.config["max_new_token"]):
                frequency_penalty += 0.1
                yield "\0"
                yield "[检测到退化，重试中]"
                # print("------------------清零------------------")
                if bool(self.config["流式输出"]) == True:
                    output = self.send_request_stream(
                        messages, frequency_penalty=frequency_penalty
                    )
                    completion_tokens = 0
                    output_text = ""
                    yield "\0"
                    for o in output:
                        if o["choices"][0]["finish_reason"] == None:
                            text_partial = o["choices"][0]["delta"]["content"]
                            if not text_partial:
                                continue
                            output_text += text_partial
                            yield text_partial
                            completion_tokens += 1
                else:
                    output = self.send_request(
                        messages, frequency_penalty=frequency_penalty
                    )
                    yield "\0"
                    for o in output:
                        completion_tokens = o["usage"]["completion_tokens"]
                        output_text = o["choices"][0]["message"]["content"]
                        yield output_text

                cnt += 1
                if cnt == 3:
                    output_text = (
                        "Error：模型无法完整输出或退化无法解决，请调大设置中的max_new_token！！！原输出："
                        + output_text
                    )
                    break
        if not (query.strip() and output_text.strip()):
            return
        self.context.append(query)
        self.context.append(output_text)
