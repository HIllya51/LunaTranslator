from translator.basetranslator_dev import basetransdev
import time, os


class commonllmdev(basetransdev):
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

    def injectjs(self):
        with open(
            os.path.join(os.path.dirname(__file__), self.jsfile),
            "r",
            encoding="utf8",
        ) as ff:
            js = ff.read() % (
                self.function1,
                self.function2,
            )
        self.Runtime_evaluate(js)

    def dotranslate(self, content): ...

    def translate(self, content):
        self.injectjs()

        if self.config["use_custom_prompt"]:
            prompt = self.config["custom_prompt"]
        else:
            prompt = "You are a translator. Please help me translate the following {} text into {}, and you should only tell me the translation.\n".format(
                self.srclang, self.tgtlang
            )
        content = prompt + content
        self.dotranslate(content)
        if self.config["usingstream"]:
            curr = ""
            while not self.Runtime_evaluate("hasdone")["result"]["value"]:
                time.sleep(0.1)
                thistext = self.Runtime_evaluate("thistext")["result"]["value"]
                if thistext.startswith(curr):
                    yield thistext[len(curr) :]
                else:
                    yield thistext
                curr = thistext
        else:
            while not self.Runtime_evaluate("hasdone")["result"]["value"]:
                time.sleep(0.1)
                continue
            yield self.Runtime_evaluate("thistext")["result"]["value"]
