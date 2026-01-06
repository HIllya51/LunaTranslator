from myutils.config import urlpathjoin
from tts.basettsclass import TTSbase, SpeechParam
from gui.customparams import getcustombodyheaders
from gui.customparams import customparams as customparams
import requests
import json
import re


class TTS(TTSbase):
    arg_support_pitch = False

    def getvoicelist(self):
        if self.config["APITYPE"] == "gptsovits":
            return [""], [""]
        elif self.config["APITYPE"] == "gsvi":
            return self.getvoicelist_gsvi()

    def speak(self, content, voice, param: SpeechParam):

        if param.speed > 0:
            speed_facter = 1.0 + param.speed / 5.0
        else:
            speed_facter = 1.0 + param.speed / 15.0

        if self.config["APITYPE"] == "gptsovits":
            return self.speak_gptsovits(content, voice, speed_facter)
        elif self.config["APITYPE"] == "gsvi":
            return self.speak_gsvi(content, voice, speed_facter)

    def speak_gptsovits(self, content, voice, speed):
        query = dict(text=content, streaming_mode=True)
        if self.config["apiv"] == "v2":
            url = urlpathjoin(self.config["URL"], "tts")
            query.update(text_lang=self.srclang, speed_factor=speed)
        else:
            url = self.config["URL"]
            query.update(text_language=self.srclang, speed=speed)
        extrabody, extraheader = getcustombodyheaders(
            self.config.get("customparams"), **locals()
        )
        headers = {"ngrok-skip-browser-warning": "true"}
        headers.update(extraheader)
        query.update(extrabody)
        response = self.proxysession.get(
            url, headers=headers, params=query, stream=True
        )
        return response

    def get_supported_versions(self, base_url: str) -> "list[str]":
        version_url = urlpathjoin(base_url, "version")
        default_version = self.config.get("apiv", "v2ProPlus")
        fallback_versions = [default_version]

        try:
            response = self.proxysession.get(version_url, timeout=5)
            status_code = response.status_code
            try:
                response_json = response.json()
            except json.JSONDecodeError:
                response_json = None
            response.raise_for_status()

            versions = []
            if isinstance(response_json, list):
                versions = [str(v) for v in response_json]
            elif isinstance(response_json, dict):
                versions = [
                    str(v)
                    for v in response_json.get("support_versions", [])
                    or response_json.get("versions", [])
                ]

            if not versions:
                versions = fallback_versions

            return sorted(list(set(versions)))

        except requests.RequestException:
            return fallback_versions
        except Exception:
            return fallback_versions

    def getvoicelist_gsvi(self) -> "tuple[list[str], list[str]]":
        base_url = self.config["URL"]
        supported_versions = self.get_supported_versions(base_url)

        all_display_names = []
        all_internal_ids = []
        models_url = urlpathjoin(base_url, "models")

        for version in supported_versions:
            request_data = {"version": version}

            try:
                response = self.proxysession.post(
                    models_url, json=request_data, timeout=10
                )
                status_code = response.status_code
                try:
                    response_json = response.json()
                except json.JSONDecodeError:
                    response_json = None

                if status_code != 200:
                    continue

                models_data = response_json.get("models", {}) if response_json else {}

                if not isinstance(models_data, dict):
                    continue

                model_names = list(models_data.keys())
                for model_name in model_names:
                    display_name = "【{}】{}".format(version, model_name)

                    internal_id = display_name

                    all_display_names.append(display_name)
                    all_internal_ids.append(internal_id)

            except requests.RequestException:
                pass

        if not all_display_names:
            return ["未找到模型"], [""]

        return all_display_names, all_internal_ids

    def speak_gsvi(self, content: str, voice: str, speed_facter):

        version = self.config.get("apiv", "v2ProPlus")
        model_name = voice

        match_display = re.match(r"【(.+?)】(.+)", voice)
        if match_display:
            version = match_display.group(1)
            model_name = match_display.group(2)
        else:
            pass

        LANG_MAP = {
            "ja": "日语",
            "zh": "中文",
            "en": "英语",
        }

        text_lang = LANG_MAP.get(self.srclang, self.srclang)

        url = urlpathjoin(self.config["URL2"], "infer_single")

        prompt_text_lang = text_lang

        request_data = {
            "streaming_mode": True,
            "app_key": "",
            "dl_url": "",
            "version": version,
            "model_name": model_name,
            "prompt_text_lang": prompt_text_lang,
            "emotion": "默认",
            "text": content,
            "text_lang": text_lang,
            "top_k": 10,
            "top_p": 1.0,
            "temperature": 1.0,
            "repetition_penalty": 1.35,
            "text_split_method": "按标点符号切",
            "batch_size": 1,
            "batch_threshold": 0.75,
            "split_bucket": True,
            "fragment_interval": 0.3,
            "speed_facter": speed_facter,
            "media_type": "wav",
            "parallel_infer": True,
            "seed": -1,
            "sample_steps": 32,
            "if_sr": False,
        }

        extrabody, extraheader = getcustombodyheaders(
            self.config.get("customparams"), **locals()
        )

        headers = {"ngrok-skip-browser-warning": "true"}
        headers.update(extraheader)
        request_data.update(extrabody)

        synthesis_response = self.proxysession.post(
            url, headers=headers, json=request_data
        )
        synthesis_status_code = synthesis_response.status_code

        try:
            synthesis_response_json = synthesis_response.json()

            if synthesis_status_code == 200 and synthesis_response_json.get("msg") in [
                "success",
                "Success",
                "合成成功",
                None,
            ]:
                audio_url = synthesis_response_json.get("audio_url")

                if audio_url:

                    audio_response = self.proxysession.get(
                        audio_url, timeout=30, stream=True
                    )
                    return audio_response

        except requests.RequestException:
            pass
        except json.JSONDecodeError:
            pass
        except Exception:
            pass

        return synthesis_response
