from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://duckduckgo.com/?t=h_&q=hi&ia=chat"
    jsfile = "commonhookfetchstream.js"
    function1 = 'url.includes("duckchat/v1/chat")'
    function2 = r"""thistext += (chunk.message?chunk.message:"")"""
    textarea_selector = 'textarea[name="user-prompt"]'
    button_selector = 'button[type="submit"]'
