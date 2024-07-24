from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://chat.deepseek.com/"
    jsfile = "commonhookxhrstream.js"
    function1 = "input.endsWith('v0/chat/completions')"
    function2 = r"""const chunk = JSON.parse(line.substring(6));
                        if(!!(chunk.choices[0].delta.content))
                        thistext += chunk.choices[0].delta.content"""

    def dotranslate(self, content):
        self.Runtime_evaluate('document.querySelector("#chat-input").click()')
        self.send_keys(content)
        self.Runtime_evaluate("document.getElementsByClassName('_89d4d19')[1].click()")
