from translator.basetranslator_dev import basetransdev
import time


class TS(basetransdev):
    target_url = "https://chat.openai.com/"

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

    def getcurr(self, idx, error=False):

        res = self.wait_for_result(
            r"""document.querySelector("#__next > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main > div.flex.h-full.flex-col > div.flex-1.overflow-hidden > div > div > div > div > div:nth-child({}) > div > div > div.relative.flex.w-full.flex-col.agent-turn > div.flex-col.gap-1.md\\:gap-3 > div.flex.flex-grow.flex-col.max-w-full > div > div").textContent""".format(
                idx + 2
            )
        )
        if "This content may violate our usage policies." == res:
            if error:
                raise Exception("This content may violate our usage policies.")
            return self.last
        self.last = res
        return res

    def translate(self, content):
        self.last = ""
        idx = self.wait_for_result(
            """document.querySelector("#__next > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main > div.flex.h-full.flex-col > div.flex-1.overflow-hidden > div > div > div > div").children.length"""
        )
        content = (
            "Please help me translate the following {} text into {}, and you should only tell me the translation.\n".format(
                self.srclang, self.tgtlang
            )
            + content
        )
        self.Runtime_evaluate(
            'textarea=document.querySelector("#prompt-textarea");textarea.value="";event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);textarea=document.querySelector("textarea");textarea.value=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);'.format(
                content
            )
        )
        self.Runtime_evaluate(
            r"""document.querySelector("#__next > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main > div.flex.h-full.flex-col > div.w-full.pt-2.md\\:pt-0.dark\\:border-white\\/20.md\\:border-transparent.md\\:dark\\:border-transparent.md\\:w-\\[calc\\(100\\%-\\.5rem\\)\\] > form > div > div.flex.w-full.items-center > div > button").click()"""
        )

        if self.config["流式输出"] == False:

            self.wait_for_result(
                r"""document.querySelector("#__next > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main > div.flex.h-full.flex-col > div.flex-1.overflow-hidden > div > div > div > div > div:nth-child({}) > div > div > div.relative.flex.w-full.flex-col.agent-turn > div.flex-col.gap-1.md\\:gap-3 > div.mt-1.flex.justify-start.gap-3.empty\\:hidden > div > span > button").innerHTML""".format(
                    idx + 2
                ),
                None,
            )  # copy button

            yield self.getcurr(idx, True)
        else:
            currtext = ""
            tutuku = True
            while tutuku:
                time.sleep(0.01)  # get text before violate usage policies.

                tutuku = (
                    "value"
                    in self.Runtime_evaluate(
                        r"""document.querySelector("#__next > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main > div.flex.h-full.flex-col > div.flex-1.overflow-hidden > div > div > div > div > div:nth-child({}) > div > div > div.relative.flex.w-full.flex-col.agent-turn > div.flex-col.gap-1.md\\:gap-3 > div.mt-1.flex.justify-start.gap-3.empty\\:hidden > div > span > button")""".format(
                            idx + 2
                        )
                    )["result"]
                )

                newcurr = self.getcurr(idx)
                yield newcurr[len(currtext) :]
                currtext = newcurr
