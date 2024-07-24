from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://chatglm.cn/main/alltoolsdetail"
    jsfile = "commonhookfetchstream.js"
    function1 = 'input.endsWith("assistant/stream")'
    function2 = """const chunk = JSON.parse(line.substring(6)); 
                         thistext = chunk.parts[0].content[0].text"""

    def dotranslate(self, content):
        self.Runtime_evaluate(
            'document.querySelector("#search-input-box > div.input-wrap.flex.flex-x-between.flex-y-center > div.input-box-inner > textarea").focus()'
        )
        self.send_keys(content)

        self.Runtime_evaluate(
            """document.querySelector("#search-input-box > div.input-wrap.flex.flex-x-between.flex-y-center > div.enter.m-three-row > img").click()"""
        )
