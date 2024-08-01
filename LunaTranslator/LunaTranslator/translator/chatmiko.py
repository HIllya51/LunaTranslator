from translator.gptcommon import gptcommon


class TS(gptcommon):

    def createheaders(self):
        return {
            "Authorization": "Bearer apiKey",
            "origin": "https://chatmiko.com",
        }

    def createurl(self):
        return "https://api.chatmiko.com/v1/chat/completions"
