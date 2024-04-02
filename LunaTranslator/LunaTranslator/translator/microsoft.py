from urllib.parse import quote
import json
from translator.basetranslator import basetrans
import base64, datetime
import json
import hashlib
import hmac, uuid
from datetime import datetime
from urllib.parse import quote
import json
from urllib.parse import quote
import json


def translate_async(text, to_language, from_language=None, self=None):
    _apiEndpoint = "api.cognitive.microsofttranslator.com"
    _apiVersion = "3.0"
    url = "{}/translate?api-version={}&to={}".format(
        _apiEndpoint, _apiVersion, to_language
    )
    if from_language is not None:
        url += "&from={}".format(from_language)
    _privateKey = [
        0xA2,
        0x29,
        0x3A,
        0x3D,
        0xD0,
        0xDD,
        0x32,
        0x73,
        0x97,
        0x7A,
        0x64,
        0xDB,
        0xC2,
        0xF3,
        0x27,
        0xF5,
        0xD7,
        0xBF,
        0x87,
        0xD9,
        0x45,
        0x9D,
        0xF0,
        0x5A,
        0x09,
        0x66,
        0xC6,
        0x30,
        0xC6,
        0x6A,
        0xAA,
        0x84,
        0x9A,
        0x41,
        0xAA,
        0x94,
        0x3A,
        0xA8,
        0xD5,
        0x1A,
        0x6E,
        0x4D,
        0xAA,
        0xC9,
        0xA3,
        0x70,
        0x12,
        0x35,
        0xC7,
        0xEB,
        0x12,
        0xF6,
        0xE8,
        0x23,
        0x07,
        0x9E,
        0x47,
        0x10,
        0x95,
        0x91,
        0x88,
        0x55,
        0xD8,
        0x17,
    ]
    headers = {
        "X-MT-Signature": get_signature(url, _privateKey),
        "Content-Type": "application/json",
    }
    json_data = [{"Text": text}]
    response = self.session.post(
        "https://{}".format(url),
        headers=headers,
        data=json.dumps(json_data).encode("utf-8"),
    )

    response.raise_for_status()

    data_json = response.json()
    root = data_json[0]["translations"][0]["text"]
    return root


def get_signature(url, private_key):
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


def try_get_expiration_date(element, expiration_date):
    token = element.get_string()
    span = token.as_span()
    index = span.index(".")
    last_index = span.last_index_of(".")

    if index != -1 and index < last_index:
        encoded_payload = token[index + 1 : last_index]
        payload = base64_url_decode(encoded_payload)

        document = json.loads(payload.decode("utf-8"))
        if "exp" in document and isinstance(document["exp"], int):
            expiration_date = datetime.utcfromtimestamp(document["exp"])
            return True

    expiration_date = None
    return False


def base64_url_decode(text):
    padding = 3 - (len(text) + 3) % 4
    if padding > 0:
        text += "=" * padding

    return base64.b64decode(text.replace("-", "+").replace("_", "/"))


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN", "cht": "zh-TW"}

    def translate(self, content):

        return translate_async(content, self.tgtlang, self.srclang, self)
