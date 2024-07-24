from translator.basetranslator_dev import basetransdev
import time, os


class TS(basetransdev):
    target_url = "https://kimi.moonshot.cn/"

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
            os.path.join(os.path.dirname(__file__), "commonhookfetchstream.js"),
            "r",
            encoding="utf8",
        ) as ff:
            js = ff.read() % (
                'input.endsWith("completion/stream")',
                """const chunk = JSON.parse(line.substring(6)); 
                        if(chunk.event!='cmpl')continue;
                        if(chunk.text)
                            thistext += chunk.text""",
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
            'document.querySelector("#root > div.MuiBox-root.css-qmryj6 > div > div.layoutContent___NvxZ_ > div.MuiBox-root.css-ar9pyi > div > div > div > div.MuiBox-root.css-8atqhb > div.chatInput___bMC0h.matchHomePageLayout___WewPT > div > div > div.editor___KShcc.editor___DSPKC.matchHomePageLayout___XTlpC > div")? document.querySelector("#root > div.MuiBox-root.css-qmryj6 > div > div.layoutContent___NvxZ_ > div.MuiBox-root.css-ar9pyi > div > div > div > div.MuiBox-root.css-8atqhb > div.chatInput___bMC0h.matchHomePageLayout___WewPT > div > div > div.editor___KShcc.editor___DSPKC.matchHomePageLayout___XTlpC > div").click() : document.querySelector("#root > div.MuiBox-root.css-qmryj6 > div > div.layoutContent___NvxZ_ > div.MuiBox-root.css-ar9pyi > div > div > div > div > div.chatPageLayoutRightBoxLeft___taL5l > div.content___inD6V > div > div.chatBottom___jS9Jd.MuiBox-root.css-jdjpte > div.chatInput___bMC0h.matchHomePageLayout___WewPT > div > div > div.editor___KShcc.editor___DSPKC.matchHomePageLayout___XTlpC > div.editorContentEditable___FZJd9").click()'
        )
        self.send_keys(content)
        self.wait_for_result('document.querySelector("#send-button").disabled', True)
        self.Runtime_evaluate("""document.querySelector("#send-button").click()""")
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
