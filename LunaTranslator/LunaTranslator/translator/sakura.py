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
        self.history = {"ja": [], "zh": []}
        self.session = requests.Session()

    def sliding_window(self, text_ja, text_zh):
        if text_ja == "" or text_zh == "":
            return
        self.history["ja"].append(text_ja)
        self.history["zh"].append(text_zh)
        if len(self.history["ja"]) > int(self.config["append_context_num"]) + 1:
            del self.history["ja"][0]
            del self.history["zh"][0]

    def get_history(self, key):
        prompt = ""
        for q in self.history[key]:
            prompt += q + "\n"
        prompt = prompt.strip()
        return prompt

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
            dst = gpt["dst"]
            info = gpt["info"] if "info" in gpt.keys() else None
            if info:
                single = f"{src}->{dst} #{info}"
            else:
                single = f"{src}->{dst}"
            gpt_dict_text_list.append(single)

        gpt_dict_raw_text = "\n".join(gpt_dict_text_list)
        return gpt_dict_raw_text

    def make_messages(
        self, query, history_ja=None, history_zh=None, gpt_dict=None, **kwargs
    ):
        if self.config["prompt_version"] == 0:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。",
                }
            ]
            if history_ja:
                messages.append(
                    {
                        "role": "user",
                        "content": f"将下面的日文文本翻译成中文：{history_ja}",
                    }
                )
            if history_zh:
                messages.append({"role": "assistant", "content": history_zh})

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
            if history_ja:
                messages.append(
                    {
                        "role": "user",
                        "content": f"将下面的日文文本翻译成中文：{history_ja}",
                    }
                )
            if history_zh:
                messages.append({"role": "assistant", "content": history_zh})

            content = ""

            gpt_dict_raw_text = self.make_gpt_dict_text(gpt_dict)
            if self.needzhconv:
                gpt_dict_raw_text = zhconv.convert(gpt_dict_raw_text, "zh-cn")
            content += "根据以下术语表（可以为空）：\n" + gpt_dict_raw_text + "\n\n"

            content += (
                "将下面的日文文本根据上述术语表的对应关系和备注翻译成中文：" + query
            )
            # print(content)
            messages.append({"role": "user", "content": content})
        return messages

    def send_request(self, query, is_test=False, **kwargs):
        extra_query = {
            "do_sample": bool(self.config["do_sample"]),
            "num_beams": int(self.config["num_beams"]),
            "repetition_penalty": float(self.config["repetition_penalty"]),
        }
        messages = self.make_messages(query, **kwargs)

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

    def send_request_stream(self, query, is_test=False, **kwargs):
        extra_query = {
            "do_sample": bool(self.config["do_sample"]),
            "num_beams": int(self.config["num_beams"]),
            "repetition_penalty": float(self.config["repetition_penalty"]),
        }
        messages = self.make_messages(query, **kwargs)

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

        for o in output.iter_lines():
            try:
                res = o.decode("utf-8").strip()[6:]  # .replace("data: ", "")
                # print(res)
                if res == "":
                    continue
                res = json.loads(res)
            except:
                raise Exception(o)

            yield res

    def translate(self, query):
        query = json.loads(query)
        gpt_dict = query["gpt_dict"]
        contentraw = query["contentraw"]
        query = query["text"]
        if gpt_dict is not None:
            query = contentraw
        self.checkempty(["API接口地址"])
        self.get_client(self.config["API接口地址"])
        frequency_penalty = float(self.config["frequency_penalty"])
        if not bool(self.config["use_context"]):
            if bool(self.config["流式输出"]) == True:
                output = self.send_request_stream(query, gpt_dict=gpt_dict)
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
                output = self.send_request(query, gpt_dict=gpt_dict)
                for o in output:
                    completion_tokens = o["usage"]["completion_tokens"]
                    output_text = o["choices"][0]["message"]["content"]
                    yield output_text

            if bool(self.config["fix_degeneration"]):
                cnt = 0
                # print(completion_tokens)
                while completion_tokens == int(self.config["max_new_token"]):
                    # detect degeneration, fixing
                    frequency_penalty += 0.1
                    yield "\0"
                    yield "[检测到退化，重试中]"
                    # print("------------------清零------------------")
                    if bool(self.config["流式输出"]) == True:
                        output = self.send_request_stream(
                            query,
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
                            query,
                            frequency_penalty=frequency_penalty,
                            gpt_dict=gpt_dict,
                        )
                        yield "\0"
                        for o in output:
                            completion_tokens = o["usage"]["completion_tokens"]
                            output_text = o["choices"][0]["message"]["content"]
                            yield output_text

                    # output = self.send_request(query, frequency_penalty=frequency_penalty)
                    # completion_tokens = output["usage"]["completion_tokens"]
                    # output_text = output["choices"][0]["message"]["content"]
                    cnt += 1
                    if cnt == 2:
                        break
        else:
            # 实验性功能，测试效果后决定是否加入。
            # fallback = False
            # if self.config['启用日文上下文模式']:
            #     history_prompt = self.get_history('ja')
            #     output = self.send_request(history_prompt + "\n" + query)
            #     completion_tokens = output.usage.completion_tokens
            #     output_text = output.choices[0].message.content

            #     if len(output_text.split("\n")) == len(history_prompt.split("\n")) + 1:
            #         output_text = output_text.split("\n")[-1]
            #     else:
            #         fallback = True
            # 如果日文上下文模式失败，则fallback到中文上下文模式。
            # if fallback or not self.config['启用日文上下文模式']:

            history_prompt = self.get_history("zh")
            # output = self.send_request(query, history_zh=history_prompt)
            # completion_tokens = output["usage"]["completion_tokens"]
            # output_text = output["choices"][0]["message"]["content"]

            if bool(self.config["流式输出"]) == True:
                output = self.send_request_stream(query, history_zh=history_prompt)
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
                output = self.send_request(query, history_zh=history_prompt)
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
                            query,
                            history_zh=history_prompt,
                            frequency_penalty=frequency_penalty,
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
                            query,
                            history_zh=history_prompt,
                            frequency_penalty=frequency_penalty,
                        )
                        yield "\0"
                        for o in output:
                            completion_tokens = o["usage"]["completion_tokens"]
                            output_text = o["choices"][0]["message"]["content"]
                            yield output_text

                    # output = self.send_request(query, history_zh=history_prompt, frequency_penalty=frequency_penalty)
                    # completion_tokens = output["usage"]["completion_tokens"]
                    # output_text = output["choices"][0]["message"]["content"]
                    cnt += 1
                    if cnt == 3:
                        output_text = (
                            "Error：模型无法完整输出或退化无法解决，请调大设置中的max_new_token！！！原输出："
                            + output_text
                        )
                        break
            self.sliding_window(query, output_text)
