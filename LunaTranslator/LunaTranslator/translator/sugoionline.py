from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {"en": "English", "ja": "Japanese", "zh": "Chinese", "vi": "Vietnamese"}

    def translate(self, query):

        json_data = {
            "content": {
                "input_text": query,
                "input_language": self.srclang,
                "output_language": self.tgtlang,
            },
            "message": "translate sentences",
        }

        response = self.session.post(
            "https://translation-server-proxy-7ja5f.ondigitalocean.app/", json=json_data
        )
        return response.json()[0]
