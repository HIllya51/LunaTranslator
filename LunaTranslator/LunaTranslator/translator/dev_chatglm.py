from translator.basetranslator_dev import basetransdev
import time, os


class TS(basetransdev):
    target_url = "https://chatglm.cn/main/alltoolsdetail"

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
        if self.Runtime_evaluate("window.injectedjs")["result"]["type"] != "undefined":
            print(self.Runtime_evaluate("window.injectedjs")["result"]["type"])
            return
        with open(
            os.path.join(os.path.dirname(__file__), "commonhookfetchstream.js"),
            "r",
            encoding="utf8",
        ) as ff:
            js = ff.read() % (
                'input.endsWith("assistant/stream")',
                """const chunk = JSON.parse(line.substring(6)); 
                         thistext = chunk.parts[0].content[0].text""",
            )
        self.Runtime_evaluate(js)
        self.Runtime_evaluate("window.injectedjs=true")

    def translate(self, content):
        self.injectjs()

        self.Runtime_evaluate("hasdone=false")
        self.Runtime_evaluate('thistext=""')
        if self.config["use_custom_prompt"]:
            prompt = self.config["custom_prompt"]
        else:
            prompt = "You are a translator. Please help me translate the following {} text into {}, and you should only tell me the translation.\n".format(
                self.srclang, self.tgtlang
            )
        content = prompt + content
        self.Runtime_evaluate(
            'document.querySelector("#search-input-box > div.input-wrap.flex.flex-x-between.flex-y-center > div.input-box-inner > textarea").click()'
        )
        self.send_keys(content)
         
        self.Runtime_evaluate("""document.querySelector("#search-input-box > div.input-wrap.flex.flex-x-between.flex-y-center > div.enter.m-three-row > img").click()""")
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
