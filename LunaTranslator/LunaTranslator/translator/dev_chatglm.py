from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://chatglm.cn/main/alltoolsdetail"
    jsfile = "commonhookfetchstream.js"
    function1 = 'url.endsWith("assistant/stream")'
    function2 = """thistext = chunk.parts[0].content[0].text"""
    textarea_selector = "#search-input-box > div.input-wrap.flex.flex-x-between.flex-y-center > div.input-box-inner > textarea"
    button_selector = "#search-input-box > div.input-wrap.flex.flex-x-between.flex-y-center > div.enter.m-three-row > img"
