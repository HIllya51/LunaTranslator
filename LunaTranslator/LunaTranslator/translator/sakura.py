from translator.basetranslator import basetrans
import requests
import json, zhconv

# OpenAI
# from openai import OpenAI


class TS(basetrans):
    using_gpt_dict = True

    def langmap(self):
        return {"zh": "zh-CN"}

    def __init__(self, typename):
        super().__init__(typename)
        self.context = []
        self.session = requests.Session()

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

    def make_gpt_dict_text(self, gpt_dict):
        if gpt_dict is None:
            return ""
        gpt_dict_text_list = []
        for gpt in gpt_dict:
            src = gpt["src"]
            if self.needzhconv:
                dst = zhconv.convert(gpt["dst"], "zh-hans")
                info = (
                    zhconv.convert(gpt["info"], "zh-hans")
                    if "info" in gpt.keys()
                    else None
                )
            else:
                dst = gpt["dst"]
                info = gpt["info"] if "info" in gpt.keys() else None

            if info:
                single = f"{src}->{dst} #{info}"
            else:
                single = f"{src}->{dst}"
            gpt_dict_text_list.append(single)

        gpt_dict_raw_text = "\n".join(gpt_dict_text_list)
        return gpt_dict_raw_text

    def appendcontext(self, message, contextnum):

        for _i in range(min(len(self.context) // 2, contextnum)):
            i = len(self.context) // 2 - min(len(self.context) // 2, contextnum) + _i
            message.append(self.context[i * 2])
            message.append(self.context[i * 2 + 1])

    def make_messages(self, query, gpt_dict=None):
        contextnum = (
            self.config["append_context_num"] if self.config["use_context"] else 0
        )
        if self.config["prompt_version"] == 0:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。",
                }
            ]
            self._gpt_common_parse_context(messages, self.context, contextnum)
            messages.append(
                {"role": "user", "content": f"将下面的日文文本翻译成中文：{query}"}
            )
        elif self.config["prompt_version"] == 1:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个轻小说翻译模型，可以流畅通顺地使用给定的术语表以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，注意不要混淆使役态和被动态的主语和宾语，不要擅自添加原文中没有的代词，也不要擅自增加或减少换行。",
                }
            ]
            self._gpt_common_parse_context(messages, self.context, contextnum)
            gpt_dict_raw_text = self.make_gpt_dict_text(gpt_dict)
            content = (
                "根据以下术语表（可以为空）：\n"
                + gpt_dict_raw_text
                + "\n\n"
                + "将下面的日文文本根据上述术语表的对应关系和备注翻译成中文："
                + query
            )
            messages.append({"role": "user", "content": content})
        elif self.config["prompt_version"] == 2:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。",
                }
            ]
            self._gpt_common_parse_context(messages, self.context, contextnum)
            gpt_dict_raw_text = self.make_gpt_dict_text(gpt_dict)
            if gpt_dict_raw_text:
                content = (
                    "根据以下术语表（可以为空）：\n"
                    + gpt_dict_raw_text
                    + "\n"
                    + "将下面的日文文本根据对应关系和备注翻译成中文："
                    + query
                )
            else:
                content = "将下面的日文文本翻译成中文：" + query
            messages.append({"role": "user", "content": content})
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
            model="sukinishiro",
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
            output = self.session.post(self.api_url + "/chat/completions", json=data)

        except requests.RequestException as e:
            raise ValueError(f"连接到Sakura API超时：{self.api_url}")
        try:
            yield output.json()
        except:
            raise Exception(output.text)

    def send_request_stream(self, messages, is_test=False, **kwargs):
        extra_query = {
            "do_sample": bool(self.config["do_sample"]),
            "num_beams": int(self.config["num_beams"]),
            "repetition_penalty": float(self.config["repetition_penalty"]),
        }

        # OpenAI
        # output = self.client.chat.completions.create(
        data = dict(
            model="sukinishiro",
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
            output = self.session.post(
                self.api_url + "/chat/completions",
                json=data,
                stream=True,
            )
        except requests.RequestException:
            raise ValueError(f"连接到Sakura API超时：{self.api_url}")
        if not output.headers["Content-Type"].startswith("text/event-stream"):
            raise Exception(output.text)
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

    def translate(self, query):
        query = json.loads(query)
        gpt_dict = query["gpt_dict"]
        contentraw = query["contentraw"]
        query = query["text"]
        if (
            (gpt_dict is not None)
            and len(gpt_dict)
            and self.config["prompt_version"] == 1
        ):
            query = contentraw
        self.checkempty(["API接口地址"])
        self.get_client(self.config["API接口地址"])
        frequency_penalty = float(self.config["frequency_penalty"])

        messages = self.make_messages(query)
        if bool(self.config["流式输出"]) == True:
            output = self.send_request_stream(messages, gpt_dict=gpt_dict)
            completion_tokens = 0
            output_text = ""
            for o in output:
                if o["choices"][0]["finish_reason"] == None:
                    text_partial = o["choices"][0]["delta"].get("content", "")
                    output_text += text_partial
                    yield text_partial
                    completion_tokens += 1
                else:
                    finish_reason = o["choices"][0]["finish_reason"]
        else:
            output = self.send_request(messages, gpt_dict=gpt_dict)
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
                        messages,
                        frequency_penalty=frequency_penalty,
                        gpt_dict=gpt_dict,
                    )
                    completion_tokens = 0
                    output_text = ""
                    yield "\0"
                    for o in output:
                        if o["choices"][0]["finish_reason"] == None:
                            text_partial = o["choices"][0]["delta"]["content"]
                            output_text += text_partial
                            yield text_partial
                            completion_tokens += 1
                        else:
                            finish_reason = o["choices"][0]["finish_reason"]
                else:
                    output = self.send_request(
                        messages,
                        frequency_penalty=frequency_penalty,
                        gpt_dict=gpt_dict,
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

        self.context.append(messages[-1])
        self.context.append({"role": "assistant", "content": output_text})
