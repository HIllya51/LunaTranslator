from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://chatgpt.com/"
    jsfile = "commonhookfetchstream.js"
    function1 = 'url.includes("conversation")'
    function2 = r"""thistext += typeof(chunk.v)=='string'?chunk.v:(chunk.v[0]?(chunk.v[0].o=='append'?chunk.v[0].v:''):'')"""
    textarea_selector = "#prompt-textarea"
    button_selector = 'button[data-testid="send-button"]'
