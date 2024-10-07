from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):
    target_url = "https://beta.theb.ai/home"
    jsfile = "commonhookfetchstream.js"
    function1 = 'url.includes("api/conversation")'
    function2 = "thistext = chunk.args.content"
    button_selector = r"#INPUT > div > div.max-w-\[66rem\].m-auto.z-2.border-2.border-n-3.rounded-xl.overflow-hidden.dark\:border-n-5.bg-white.dark\:bg-n-6 > div > button.group.absolute.right-3.bottom-2.rounded-xl.transition-colors.disabled\:bg-slate-400.disabled\:hover\:bg-slate-400.disabled\:cursor-no-drop.w-10.h-10.bg-primary-1.hover\:bg-primary-1\/90"
    textarea_selector = "#textareaAutosize"
