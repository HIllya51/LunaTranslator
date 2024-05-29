from translator.basetranslator import basetrans
import re


class TS(basetrans):
    def langmap(self):
        return {
            "zh": "Simplified Chinese",
            "ja": "Japanese",
            "en": "English",
            "ru": "Russian",
            "es": "Spanish",
            "ko": "Korean",
            "fr": "French",
            "cht": "Traditional Chinese",
            "vi": "Vietnamese",
            "tr": "Turkish",
            "pl": "Polish",
            "uk": "Ukrainian",
            "it": "Italian",
            "ar": "Arabic",
            "th": "Thai",
        }

    def translate(self, content):
        if self.config["使用自定义promt"]:
            prompt = self.config["自定义promt"]
        else:
            prompt = "You are a translator. Please help me translate the following {} text into {}, and you should only tell me the translation.".format(
                self.srclang, self.tgtlang
            )
        res = self.session.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            params={"key": self.config["api-key"]},
            json={
                "contents": [
                    {"role": "user", "parts": [{"text": prompt + "\n" + content}]}
                ],
                "generation_config": {"candidate_count": 1, "temperature": 0.4},
                "safety_settings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_NONE",
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_NONE",
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE",
                    },
                ],
            },
            verify=False,
        )
        try:
            res = res.json()
        except:
            raise Exception(res.text)
        try:
            line = res["candidates"][0]["content"]["parts"][0]["text"]
            return line
        except:
            print(res)
            raise Exception("Error")
