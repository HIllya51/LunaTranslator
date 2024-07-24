from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://kimi.moonshot.cn/"
    jsfile = "commonhookfetchstream.js"
    function1 = 'input.endsWith("completion/stream")'
    function2 = """const chunk = JSON.parse(line.substring(6)); 
                        if(chunk.event!='cmpl')continue;
                        if(chunk.text)
                            thistext += chunk.text"""

    def dotranslate(self, content):
        self.Runtime_evaluate(
            'document.querySelector("#root > div.MuiBox-root.css-qmryj6 > div > div.layoutContent___NvxZ_ > div.MuiBox-root.css-ar9pyi > div > div > div > div.MuiBox-root.css-8atqhb > div.chatInput___bMC0h.matchHomePageLayout___WewPT > div > div > div.editor___KShcc.editor___DSPKC.matchHomePageLayout___XTlpC > div")? document.querySelector("#root > div.MuiBox-root.css-qmryj6 > div > div.layoutContent___NvxZ_ > div.MuiBox-root.css-ar9pyi > div > div > div > div.MuiBox-root.css-8atqhb > div.chatInput___bMC0h.matchHomePageLayout___WewPT > div > div > div.editor___KShcc.editor___DSPKC.matchHomePageLayout___XTlpC > div").click() : document.querySelector("#root > div.MuiBox-root.css-qmryj6 > div > div.layoutContent___NvxZ_ > div.MuiBox-root.css-ar9pyi > div > div > div > div > div.chatPageLayoutRightBoxLeft___taL5l > div.content___inD6V > div > div.chatBottom___jS9Jd.MuiBox-root.css-jdjpte > div.chatInput___bMC0h.matchHomePageLayout___WewPT > div > div > div.editor___KShcc.editor___DSPKC.matchHomePageLayout___XTlpC > div.editorContentEditable___FZJd9").click()'
        )
        self.send_keys(content)
        self.wait_for_result('document.querySelector("#send-button").disabled', True)
        self.Runtime_evaluate("""document.querySelector("#send-button").click()""")
