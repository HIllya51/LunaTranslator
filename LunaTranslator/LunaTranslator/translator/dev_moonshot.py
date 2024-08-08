from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://kimi.moonshot.cn/"
    jsfile = "commonhookfetchstream.js"
    function1 = 'url.endsWith("completion/stream")'
    function2 = """if(chunk.event!='cmpl')continue;
                        if(chunk.text)
                            thistext += chunk.text"""
    button_selector='#send-button'
    textarea_selector='#root > div > div.mainContent___vvQdb > div.layoutContent___NvxZ_ > div.MuiBox-root.css-ar9pyi > div > div > div > div > div.chatPageLayoutRightBoxLeft___taL5l > div.content___inD6V > div > div.chatBottomContainer___MmYFg.MuiBox-root.css-0 > div > div.chatInput___bMC0h > div > div > div.editor___KShcc.editor___DSPKC > div.editorContentEditable___FZJd9'