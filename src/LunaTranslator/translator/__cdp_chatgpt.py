from translator.basetranslator import basetrans
from translator.cdp_helper import cdp_helperllm
from language import Languages


class chatgpt(cdp_helperllm):
    target_url = "https://chatgpt.com/"
    jsfile = "commonhookfetchstream.js"
    function1 = 'url.includes("conversation")'
    function2 = r"""thistext += typeof(chunk.v)=='string'?chunk.v:(chunk.v[0]?(chunk.v[0].o=='append'?chunk.v[0].v:''):'')"""
    textarea_selector = "#prompt-textarea"
    button_selector = 'button[data-testid="send-button"]'


class chatgpt_mirror(cdp_helperllm):

    @property
    def target_url(self):
        return self.config["target_url"]

    @property
    def jsfile(self):
        return ["commonhookfetchstream.js", "commonhookxhrstream"][
            self.config["request_method"]
        ]

    @property
    def function1(self):
        return self.config["checkneturlfunction"]

    @property
    def function2(self):
        return self.config["extracttextfunction"]

    @property
    def button_selector(self):
        return self.config["button_selector"]

    @property
    def textarea_selector(self):
        return self.config["textarea_selector"]


class TS(basetrans):

    def langmap(self):
        return Languages.createenglishlangmap()

    def init(self):
        self.devtool = None
        self.checkinterface()

    def checkinterface(self):
        if (self.config["usewhich"] == 0) and (not isinstance(self.devtool, chatgpt)):
            self.devtool = chatgpt(self)
        elif (self.config["usewhich"] == 1) and (
            not isinstance(self.devtool, chatgpt_mirror)
        ):
            self.devtool = chatgpt_mirror(self)

    def translate(self, content):
        self.checkinterface()
        return self.devtool.translate(content)
