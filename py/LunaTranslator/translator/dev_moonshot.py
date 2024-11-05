from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://kimi.moonshot.cn/"
    jsfile = "commonhookfetchstream.js"
    function1 = 'url.endsWith("completion/stream")'
    function2 = """if(chunk.event!='cmpl')continue;
                        if(chunk.text)
                            thistext += chunk.text"""
    button_selector='#send-button'
    textarea_selector='button[id="send-button"]'