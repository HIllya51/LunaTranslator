import requests
import time, os
from tts.basettsclass import TTSbase
from urllib.parse import quote
from typing import List, Tuple
import re

class TTS(TTSbase):
    def getvoicelist(self):
        responseVits = requests.get(
            f"http://127.0.0.1:{self.config['Port']}/voice/speakers"
        ).json()
        self.voicelist = []

        # 获取所有模型类型，对于每个模型类型下的模型信息，将其 modelType、id、name 合成一个字符串
        modelTypes = responseVits.keys()
        for modelType in modelTypes:
            vits_data = responseVits[modelType]
            for item in vits_data:
                model_info = f'{modelType}_{item["id"]}_{item["name"]}'
                self.voicelist.append(model_info)
        return self.voicelist

    def voiceshowmap(self, voice):
        return voice

    def speak(self, content, rate, voice, voiceidx):
        # 原本的推理模式
        if int(self.config["mode"]) == 0:
            return self._speak_mode1(content, voice)
        # 语种识别的推理模式
        elif int(self.config["mode"]) == 1:
            return self._speak_mode2(content, voice)
        else:
            raise ValueError("Invalid mode. Use 1 or 2.")

    def _speak_mode1(self, content, voice):
        encoded_content = quote(content)
        idx = int(voice.split("_")[1])
        model = str.lower(voice.split("_")[0])
        response = requests.get(
            f"http://127.0.0.1:{self.config['Port']}/voice/{model}?text={encoded_content}&id={idx}&lang=auto&prompt_lang=auto&format=wav&preset={self.config['preset']}"
        ).content
        return response

    def _speak_mode2(self, content, voice):
        idx = int(voice.split("_")[1])
        model = str.lower(voice.split("_")[0])
        detected_parts = self.detect_languages(content)
        
        combined_audio_data = b''

        for part, lang in detected_parts:
            encoded_part = quote(part)
            response = requests.get(
                f"http://127.0.0.1:{self.config['Port']}/voice/{model}?text={encoded_part}&id={idx}&lang={lang}&prompt_lang=auto&format=mp3&preset={self.config['preset']}"
            ).content
            
            combined_audio_data += response

        return combined_audio_data

    def detect_languages(self, text: str) -> List[Tuple[str, str]]:
        """自动检测语种类型"""
        def detect_language(segment: str) -> str:
            if re.search(r'[\u4e00-\u9fff]', segment):
                return 'zh'
            elif re.search(r'[\u3040-\u30ff\u31f0-\u31ff]', segment):
                return 'ja'
            elif re.search(r'[a-zA-ZＡ-Ｚａ-ｚ]', segment):
                return 'en'
            elif re.search(r'[0-9０-９]', segment):
                return 'zh'
            else:
                return ''

        text = text.strip()
        result = []
        current_segment = ''
        current_lang = ''
        
        for char in text:
            char_lang = detect_language(char)
            
            if char_lang == '':
                current_segment += char
            elif char_lang != current_lang:
                if current_segment:
                    result.append((current_segment, current_lang))
                current_segment = char
                current_lang = char_lang
            else:
                current_segment += char

        if current_segment:
            result.append((current_segment, current_lang))

        # 处理开头的未知语言段
        while result and result[0][1] == '':
            if len(result) > 1:
                result[1] = (result[0][0] + result[1][0], result[1][1])
                result.pop(0)
            else:
                result[0] = (result[0][0], 'zh')  # 如果整个文本都是未知语言，归类为中文

        # 合并相邻的相同语言段
        i = 0
        while i < len(result) - 1:
            if result[i][1] == result[i+1][1]:
                result[i] = (result[i][0] + result[i+1][0], result[i][1])
                result.pop(i+1)
            else:
                i += 1

        return result
