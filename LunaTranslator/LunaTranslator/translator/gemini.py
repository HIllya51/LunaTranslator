from translator.basetranslator import basetrans
import json


class TS(basetrans):
    def langmap(self):
        return {
            "zh": "Simplified Chinese",
            "ja": "Japanese",
            "en": "English",
            "ru": "Russian",
            "es": "Spanish",
            "ko": "Korean",
            "fr": "French",
            "cht": "Traditional Chinese",
            "vi": "Vietnamese",
            "tr": "Turkish",
            "pl": "Polish",
            "uk": "Ukrainian",
            "it": "Italian",
            "ar": "Arabic",
            "th": "Thai",
        }

    def __init__(self, typename):
        self.context = []
        super().__init__(typename)

    def inittranslator(self):
        self.api_key = None

    def translate(self, query):
        self.checkempty(["SECRET_KEY", "model"])
        self.contextnum = int(self.config["context"])

        gen_config = {
            "generationConfig": {
                "stopSequences": [" \n"],
                "temperature": self.config["Temperature"],
            }
        }
        model = self.config["model"]
        user_prompt = (
            self.config.get("user_user_prompt", "")
            if self.config.get("use_user_user_prompt", False)
            else ""
        )
        try:
            if "{sentence}" in user_prompt:
                query = user_prompt.format(sentence=query)
            else:
                query = user_prompt + query
        except:
            pass
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

        if self.config["use_custom_prompt"]:
            sys_message = {
                "systemInstruction": {"parts": {"text": self.config["custom_prompt"]}}
            }
        else:
            sys_message = {
                "systemInstruction": {
                    "parts": {
                        "text": "You are a translator. Please help me translate the following {} text into {}, and you should only tell me the translation.".format(
                            self.srclang, self.tgtlang
                        ),
                    },
                },
            }
        message = []
        for _i in range(min(len(self.context) // 2, self.contextnum)):
            i = (
                len(self.context) // 2
                - min(len(self.context) // 2, self.contextnum)
                + _i
            )
            message.append(self.context[i * 2])
            message.append(self.context[i * 2 + 1])

        message.append({"role": "user", "parts": [{"text": query}]})
        contents = dict(contents=message)
        usingstream = self.config["usingstream"]
        payload = {**contents, **safety, **sys_message, **gen_config}
        res = self.proxysession.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:{['generateContent','streamGenerateContent'][usingstream]}",
            params={"key": self.multiapikeycurrent["SECRET_KEY"]},
            json=payload,
            stream=usingstream,
        )
        if usingstream:
            line = ""
            for __x in res.iter_lines(decode_unicode=True):
                __x = __x.strip()
                if not __x.startswith('"text":'):
                    continue
                __x = json.loads("{" + __x + "}")["text"]
                yield __x
                line += __x

        else:
            try:
                line = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            except:
                raise Exception(res.text)
            yield line
        self.context.append({"role": "user", "parts": [{"text": query}]})
        self.context.append({"role": "model", "parts": [{"text": line}]})
