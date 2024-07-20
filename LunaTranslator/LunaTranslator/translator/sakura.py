from translator.basetranslator import basetrans
import requests
import json

# OpenAI
# from openai import OpenAI


class TS(basetrans):
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

    def make_messages(self, query, history_ja=None, history_zh=None, **kwargs):
        messages = [
            {
                "role": "system",
                "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。",
            }
        ]
        if history_ja:
            messages.append(
                {"role": "user", "content": f"将下面的日文文本翻译成中文：{history_ja}"}
            )
        if history_zh:
            messages.append({"role": "assistant", "content": history_zh})

        messages.append(
            {"role": "user", "content": f"将下面的日文文本翻译成中文：{query}"}
        )
        return messages

    def send_request(self, query, is_test=False, **kwargs):
        extra_query = {
            "do_sample": bool(self.config["do_sample"]),
            "num_beams": int(self.config["num_beams"]),
            "repetition_penalty": float(self.config["repetition_penalty"]),
        }
        messages = self.make_messages(query, **kwargs)
        try:
            # OpenAI
            # output = self.client.chat.completions.create(
            data = dict(
                model="sukinishiro",
                messages=messages,
                temperature=float(self.config["temperature"]),
                top_p=float(self.config["top_p"]),
                max_tokens=1 if is_test else int(self.config["max_new_token"]),
                frequency_penalty=(
                    float(kwargs["frequency_penalty"])
                    if "frequency_penalty" in kwargs.keys()
                    else float(self.config["frequency_penalty"])
                ),
                seed=-1,
                extra_query=extra_query,
                stream=False,
            )
            output = self.session.post(
                self.api_url + "/chat/completions", json=data
            ).json()
            yield output
        except requests.Timeout as e:
            raise ValueError(f"连接到Sakura API超时：{self.api_url}，请尝试修改参数。")

        except Exception as e:
            print(e)
            raise ValueError(
                f"无法连接到Sakura API：{self.api_url}，请检查你的API链接是否正确填写，以及API后端是否成功启动。"
            )

    def send_request_stream(self, query, is_test=False, **kwargs):
        extra_query = {
            "do_sample": bool(self.config["do_sample"]),
            "num_beams": int(self.config["num_beams"]),
            "repetition_penalty": float(self.config["repetition_penalty"]),
        }
        messages = self.make_messages(query, **kwargs)
        try:
            # OpenAI
            # output = self.client.chat.completions.create(
            data = dict(
                model="sukinishiro",
                messages=messages,
                temperature=float(self.config["temperature"]),
                top_p=float(self.config["top_p"]),
                max_tokens=1 if is_test else int(self.config["max_new_token"]),
                frequency_penalty=(
                    float(kwargs["frequency_penalty"])
                    if "frequency_penalty" in kwargs.keys()
                    else float(self.config["frequency_penalty"])
                ),
                seed=-1,
                extra_query=extra_query,
                stream=True,
            )
            output = self.session.post(
                self.api_url + "/chat/completions",
                json=data,
                stream=True,
            )
            for o in output.iter_lines(delimiter="\n\n".encode()):
                res = o.decode("utf-8").strip()[6:]  # .replace("data: ", "")
                print(res)
                if res != "":
                    yield json.loads(res)
        except requests.Timeout as e:
            raise ValueError(f"连接到Sakura API超时：{self.api_url}，请尝试修改参数。")

        except Exception as e:
            import traceback

            print(e)
            e1 = traceback.format_exc()
            raise ValueError(
                f"Error: {str(e1)}. 无法连接到Sakura API：{self.api_url}，请检查你的API链接是否正确填写，以及API后端是否成功启动。"
            )

    def translate(self, query):
        self.checkempty(["API接口地址"])
        self.get_client(self.config["API接口地址"])
        frequency_penalty = float(self.config["frequency_penalty"])
        if not bool(self.config["use_context"]):
            if bool(self.config["流式输出"]) == True:
                output = self.send_request_stream(query)
                completion_tokens = 0
                output_text = ""
                for o in output:
                    if o["choices"][0]["finish_reason"] == None:
                        text_partial = o["choices"][0]["delta"]["content"]
                        output_text += text_partial
                        yield text_partial
                        completion_tokens += 1
                    else:
                        finish_reason = o["choices"][0]["finish_reason"]
            else:
                output = self.send_request(query)
                for o in output:
                    completion_tokens = o["usage"]["completion_tokens"]
                    output_text = o["choices"][0]["message"]["content"]
                    yield output_text

            if bool(self.config["fix_degeneration"]):
                cnt = 0
                print(completion_tokens)
                while completion_tokens == int(self.config["max_new_token"]):
                    # detect degeneration, fixing
                    frequency_penalty += 0.1
                    yield "\0"
                    yield "[检测到退化，重试中]"
                    print("------------------清零------------------")
                    if bool(self.config["流式输出"]) == True:
                        output = self.send_request_stream(
                            query, frequency_penalty=frequency_penalty
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
                            query, frequency_penalty=frequency_penalty
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
                        text_partial = o["choices"][0]["delta"]["content"]
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
                print(completion_tokens)
                while completion_tokens == int(self.config["max_new_token"]):
                    frequency_penalty += 0.1
                    yield "\0"
                    yield "[检测到退化，重试中]"
                    print("------------------清零------------------")
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
