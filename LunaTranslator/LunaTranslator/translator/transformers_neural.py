from translator.basetranslator import basetrans
from transformers import pipeline


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN", "cht": "zh-TW"}

    def translate_sentence(self, sentence):
        return self.pipeline(f'<-ja2zh-> {sentence}', repetition_penalty=1.3)[0]['translation_text']

    def inittranslator(self):
        assert not self.checkempty(['模型路径','推理设备'])
        model_path = self.config['模型路径']
        device = self.config['推理设备']
        self.pipeline = pipeline("translation", model=model_path,device=device)

    def translate(self, content):
        translated = self.translate_sentence(content)
        return translated
