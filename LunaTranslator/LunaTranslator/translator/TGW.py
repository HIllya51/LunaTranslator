import requests
import json
from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN"}

    def __init__(self, typename):
        self.timeout = 30
        self.api_url = ""
        self.history = {"ja": [], "zh": []}
        super().__init__(typename)

    def sliding_window(self, text_ja, text_zh):
        if text_ja == "" or text_zh == "":
            return
        self.history["ja"].append(text_ja)
        self.history["zh"].append(text_zh)
        if (
                len(self.history["ja"])
                > int(self.config["附带上下文个数(必须打开利用上文翻译)"]) + 1
        ):
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

    def stop_words(self):
        if self.config["stop(自定义停止符，多个用逗号隔开)"]:
            stop_words = [
                word.strip()
                for word in self.config["stop(自定义停止符，多个用逗号隔开)"]
                .replace("，", ",")
                .split(",")
            ]
            return stop_words
        else:
            return []

    def make_messages(self, context, history_ja=None, history_zh=None, **kwargs):
        system_prompt = self.config["system_prompt(系统人设)"]
        prompt = self.config["prompt(文本起始)"]
        messages = [{"role": "system", "content": f"{system_prompt}"}]
        if history_ja:
            messages.append({"role": "user", "content": f"{prompt}{history_ja}"})
        if history_zh:
            messages.append({"role": "assistant", "content": history_zh})

        messages.append({"role": "user", "content": f"{prompt}{context}"})
        return messages

    def send_request(self, text, **kwargs):
        try:
            url = self.api_url + "/chat/completions"
            stop_words_result = self.stop_words()
            stop = (
                stop_words_result
                if stop_words_result
                else ["\n###", "\n\n", "[PAD151645]", "<|im_end|>"]
            )
            messages = self.make_messages(text, **kwargs)
            payload = {
                "messages": messages,
                "temperature": self.config["temperature"],
                "stop": stop,
                "stream": False,
                "instruction_template": self.config[
                    "instruction_template(需要按照模型模板选择)"
                ],
                "mode": self.config["mode"],
                "top_p": self.config["top_p"],
                "min_p": self.config["min_p"],
                "top_k": self.config["top_k"],
                "num_beams": self.config["num_beams"],
                "repetition_penalty": self.config["repetition_penalty"],
                "repetition_penalty_range": self.config["repetition_penalty_range"],
                "do_sample": self.config["do_sample"],
                "frequency_penalty": self.config["frequency_penalty"],
            }
            response = requests.post(url, timeout=self.timeout, json=payload)
            if response.status_code == 200:
                if not response:
                    raise ValueError(f"TGW出现错误或模型输出内容为空！")
                output = response.json()["choices"][0]["message"]["content"].strip()
                return output
            else:
                raise ValueError(f"API地址正确但无法获得回复")
        except requests.Timeout as e:
            raise ValueError(
                f"连接到TGW超时：{self.api_url}，当前最大连接时间为: {self.timeout}，请尝试修改参数。"
            )

        except Exception as e:
            print(e)
            raise ValueError(f"无法连接到TGW:{e}")

    def make_request_stream(self, text, **kwargs):
        stop_words_result = self.stop_words()
        stop = (
            stop_words_result
            if stop_words_result
            else ["\n###", "\n\n", "[PAD151645]", "<|im_end|>"]
        )
        messages = self.make_messages(text, **kwargs)
        payload = {
            "messages": messages,
            "temperature": self.config["temperature"],
            "stop": stop,
            "stream": True,
            "instruction_template": self.config[
                "instruction_template(需要按照模型模板选择)"
            ],
            "mode": self.config["mode"],
            "top_p": self.config["top_p"],
            "min_p": self.config["min_p"],
            "top_k": self.config["top_k"],
            "num_beams": self.config["num_beams"],
            "repetition_penalty": self.config["repetition_penalty"],
            "repetition_penalty_range": self.config["repetition_penalty_range"],
            "do_sample": self.config["do_sample"],
            "frequency_penalty": self.config["frequency_penalty"],
        }
        return payload

    def translate(self, context):
        self.checkempty(["API接口地址(默认为http://127.0.0.1:5000/)"])
        self.checkempty(["instruction_template(需要按照模型模板选择)"])
        self.timeout = self.config["API超时(秒)"]

        if self.api_url == "":
            self.get_client(self.config["API接口地址(默认为http://127.0.0.1:5000/)"])

        if self.config["流式输出"] == False:
            if not bool(self.config["利用上文信息翻译"]):
                output = self.send_request(context)
            else:
                history_prompt = self.get_history("zh")
                output = self.send_request(context, history_zh=history_prompt)
            self.sliding_window(context, output)
            yield output
        else:
            url = self.api_url + "/chat/completions"
            if not bool(self.config["利用上文信息翻译"]):
                payload = self.make_request_stream(context)
            else:
                history_prompt = self.get_history("zh")
                payload = self.make_request_stream(context, history_zh=history_prompt)

            try:
                response = requests.post(url, timeout=self.timeout, json=payload, stream=True)
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            if line.startswith(b"data: "):
                                line = line[len(b"data: "):]
                            payload = json.loads(line)
                            chunk = payload['choices'][0]['delta']['content']
                            yield chunk

                else:
                    raise ValueError(f"API无响应")
            except requests.Timeout as e:
                raise ValueError(
                    f"连接到TGW超时：{self.api_url}，当前最大连接时间为: {self.timeout}，请尝试修改参数。"
                )

            except Exception as e:
                print(e)
                raise ValueError(f"无法连接到TGW:{e}")

