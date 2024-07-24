from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://chatgpt.com/"
    jsfile = "commonhookfetchstream.js"
    function1 = 'input.includes("conversation")'
    function2 = r"""const chunk = JSON.parse(line.substring(6));
                        thistext = chunk.message.content.parts[0]"""

    def dotranslate(self, content):
        self.Runtime_evaluate(
            'textarea=document.querySelector("#prompt-textarea");textarea.value="";event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);textarea.value=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);'.format(
                content
            )
        )
        self.Runtime_evaluate(
            r"""document.querySelector("#__next > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div > main > div.flex.h-full.flex-col.focus-visible\\:outline-0 > div.md\\:pt-0.dark\\:border-white\\/20.md\\:border-transparent.md\\:dark\\:border-transparent.w-full > div.text-base.px-3.md\\:px-4.m-auto.md\\:px-5.lg\\:px-1.xl\\:px-5 > div > form > div > div.flex.w-full.items-center > div > div > button").click()"""
        )
