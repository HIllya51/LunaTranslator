from translator.gptcommon import gptcommon


class TS(gptcommon):
    def createurl(self):
        return f'https://{self.config["endpoint"]}/openai/deployments/{self.config["deployment-id"]}/completions?api-version={self.config["api-version"]}'

    def createheaders(self):
        _ = super().createheaders()
        _.update({"api-key": self.multiapikeycurrent["api-key"]})

    def translate(self, query):
        self.checkempty(["api-key", "api-version", "endpoint", "deployment-id"])
        return super().translate(query)
