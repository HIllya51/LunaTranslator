from translator.basetranslator import basetrans
from language import Languages


class TS(basetrans):

    def init(self):
        self.mostmaybelang = "jpn"
        self.host_url = "https://www.reverso.net/text-translation"
        self.api_url = "https://api.reverso.net/translate/v1/translation"
        self.language_pattern = r"https://cdn.reverso.net/trans/v(\d).(\d).(\d)/main.js"
        _ = self.proxysession.get(self.host_url)

    def reverso_api(self, __, query_text, from_language, to_language):
        form_data = {
            "format": "text",
            "from": from_language,
            "to": to_language,
            "input": query_text,
            "options": {
                "contextResults": "true",
                "languageDetection": "true",
                "sentenceSplitter": "true",
                "origin": ["translation.web", "contextweb"][__],
            },
        }
        r = self.proxysession.post(self.api_url, json=form_data)
        return r.json()

    def langmap(self):
        return {
            Languages.Chinese: "chi",
            Languages.English: "eng",
            Languages.Spanish: "spa",
            Languages.French: "fra",
            Languages.Korean: "kor",
            Languages.Russian: "rus",
            Languages.Japanese: "jpn",
        }

    def translate(self, content):
        if self.is_src_auto:
            src = self.mostmaybelang
        else:
            src = self.srclang

        data = self.reverso_api(self.config["origin"], content, src, self.tgtlang)
        if self.is_src_auto:
            det = data["languageDetection"]["detectedLanguage"]
            if det == src:
                return "".join(data["translation"])
            else:
                self.mostmaybelang = det
                data = self.reverso_api(
                    self.config["origin"], content, det, self.tgtlang
                )
                return "".join(data["translation"])
        else:
            return "".join(data["translation"])
