from urllib.parse import quote
from translator.basetranslator import basetrans
import base64, datetime
import hashlib
import hmac, uuid
from datetime import datetime
from language import Languages


class TS(basetrans):

    def get_signature(self, url, private_key):
        guid = str(uuid.uuid4()).replace("-", "")
        escaped_url = quote(url, safe="")

        dateTime = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        bytes_str = (
            "MSTranslatorAndroidApp{}{}{}".format(escaped_url, dateTime, guid)
            .lower()
            .encode("utf-8")
        )

        hash_ = hmac.new(bytes(private_key), bytes_str, hashlib.sha256).digest()

        signature = "MSTranslatorAndroidApp::{}::{}::{}".format(
            base64.b64encode(hash_).decode(), dateTime, guid
        )
        return signature

    def translate(self, text):
        _apiEndpoint = "api.cognitive.microsofttranslator.com"
        _apiVersion = "3.0"
        url = "{}/translate?api-version={}&to={}".format(
            _apiEndpoint, _apiVersion, self.tgtlang
        )
        if not self.is_src_auto:
            url += "&from={}".format(self.srclang)
        _privateKey = b"\xa2):=\xd0\xdd2s\x97zd\xdb\xc2\xf3'\xf5\xd7\xbf\x87\xd9E\x9d\xf0Z\tf\xc60\xc6j\xaa\x84\x9aA\xaa\x94:\xa8\xd5\x1anM\xaa\xc9\xa3p\x125\xc7\xeb\x12\xf6\xe8#\x07\x9eG\x10\x95\x91\x88U\xd8\x17"
        headers = {
            "X-MT-Signature": self.get_signature(url, _privateKey),
        }
        json_data = [{"Text": text}]
        response = self.proxysession.post(
            "https://{}".format(url), headers=headers, json=json_data
        )
        try:
            data_json = response.json()
            root = data_json[0]["translations"][0]["text"]
            return root
        except:
            raise Exception(response)

    def langmap(self):
        return {Languages.Chinese: "zh-CN", Languages.TradChinese: "zh-TW"}
