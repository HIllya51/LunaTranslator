from translator.gptcommon import gptcommon


class TS(gptcommon):
    def createurl(self):
        return self.config["OPENAI_API_BASE"] + self.config["Appedix"]

    def createparam(self):
        api_type = self.config["api_type"]
        if api_type in [1, 2]:
            api_version = "2023-05-15"
            return {"api-version": api_version}
        else:
            return super().createparam()

    def createheaders(self):
        api_type = self.config["api_type"]
        _ = super().createheaders()
        if api_type == 1:  # azure
            _.update({"api-key": self.multiapikeycurrent["SECRET_KEY"]})
        return _

    def translate(self, query):
        self.checkempty(["SECRET_KEY", "model"])
        return super().translate(query)
