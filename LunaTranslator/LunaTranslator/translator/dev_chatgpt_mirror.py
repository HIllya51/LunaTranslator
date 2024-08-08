from translator.dev_llm_common import commonllmdev


class TS(commonllmdev):

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
