from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://chatgpt.com/"
    jsfile = "commonhookfetchstream.js"
    function1 = 'url.includes("conversation")'
    function2 = r"""thistext = chunk.message.content.parts[0]"""
    textarea_selector = "#prompt-textarea"
    button_selector = 'button[data-testid="send-button"]'
