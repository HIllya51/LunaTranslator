from translator.basetranslator_dev import basetransdev
import time, os


class TS(basetransdev):
    target_url = "https://chatgpt.com/"

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
            return
        with open(
            os.path.join(os.path.dirname(__file__), "dev_chatgpt.js"),
            "r",
            encoding="utf8",
        ) as ff:
            js = ff.read()
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
            'textarea=document.querySelector("#prompt-textarea");textarea.value="";event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);textarea=document.querySelector("textarea");textarea.value=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);'.format(
                content
            )
        )
        self.Runtime_evaluate(
            r"""document.querySelector("#__next > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div > main > div.flex.h-full.flex-col.focus-visible\\:outline-0 > div.md\\:pt-0.dark\\:border-white\\/20.md\\:border-transparent.md\\:dark\\:border-transparent.w-full > div.text-base.px-3.md\\:px-4.m-auto.md\\:px-5.lg\\:px-1.xl\\:px-5 > div > form > div > div.flex.w-full.items-center > div > div > button").click()"""
        )
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
