from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://tongyi.aliyun.com/qianwen"
    jsfile = "commonhookfetchstream.js"
    function1 = 'input.endsWith("dialog/conversation")'
    function2 = r"""const chunk = JSON.parse(line.substring(6));
                        thistext = chunk.contents[0].content"""

    def dotranslate(self, content):
        self.Runtime_evaluate('document.getElementsByTagName("textarea")[0].focus()')
        self.send_keys(content)
        self.Runtime_evaluate(
            r"""document.querySelector("#tongyiPageLayout > div.sc-fQpRED.jsoEZg > div > div.sc-hNGPaV.erDcgy.pageContentWrap--AovzQ5wq > div > div.inputField--PE5FhWzd > div > div.chatInput--eJzBH8LP > div.operateBtn--zFx6rSR0").click()"""
        )
