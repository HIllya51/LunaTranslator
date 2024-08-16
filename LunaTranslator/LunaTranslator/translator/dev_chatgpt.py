from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://chatgpt.com/"
    jsfile = "commonhookfetchstream.js"
    function1 = 'url.includes("conversation")'
    function2 = r"""thistext = chunk.message.content.parts[0]"""
    textarea_selector = "#prompt-textarea"
    button_selector = r"#__next > div.relative.flex.h-full.w-full.overflow-hidden.transition-colors.z-0 > div > main > div.flex.h-full.flex-col.focus-visible\:outline-0 > div.md\:pt-0.dark\:border-white\/20.md\:border-transparent.md\:dark\:border-transparent.w-full > div.text-base.px-3.md\:px-4.m-auto.md\:px-5 > div > form > div > div.flex.w-full.items-center > div > div > button"
