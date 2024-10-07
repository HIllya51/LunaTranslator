from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://tongyi.aliyun.com/qianwen"
    jsfile = "commonhookfetchstream.js"
    function1 = 'url.endsWith("dialog/conversation")'
    function2 = r"""thistext = chunk.contents[0].content"""
    textarea_selector = "textarea:first-of-type"
    button_selector = ".operateBtn--zFx6rSR0"
    # 必须主动给文本框焦点
