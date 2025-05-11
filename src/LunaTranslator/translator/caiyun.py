from translator.basetranslator import basetrans
import base64
from language import Languages


def crypt(if_de=True):
    normal_key = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "0123456789" + "=.+-_/"
    )
    cipher_key = (
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm" + "0123456789" + "=.+-_/"
    )
    if if_de:
        return {k: v for k, v in zip(cipher_key, normal_key)}
    return {v: k for k, v in zip(cipher_key, normal_key)}


def encrypt(plain_text):
    encrypt_dictionary = crypt(if_de=False)
    _cipher_text = base64.b64encode(plain_text.encode()).decode()
    return "".join(list(map(lambda k: encrypt_dictionary[k], _cipher_text)))


def decrypt(cipher_text):
    _ciphertext = "".join(list(map(lambda k: crypt()[k], cipher_text)))
    return base64.b64decode(_ciphertext).decode()


class TS(basetrans):
    def langmap(self):
        return {Languages.TradChinese: "zh-Hant"}

    def init(self):

        self.token = "token:qgemv4jr1y38jyq6vhvi"
        self.bid = "beba19f9d7f10c74c98334c9e8afcd34"

    def translate(self, content):

        headers = {
            "authority": "api.interpreter.caiyunai.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "app-name": "xy",
            "cache-control": "no-cache",
            "device-id": "",
            "origin": "https://fanyi.caiyunapp.com",
            "os-type": "web",
            "os-version": "",
            "pragma": "no-cache",
            "referer": "https://fanyi.caiyunapp.com/",
            "sec-ch-ua": '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "x-authorization": self.token,
        }

        json_data = {
            "browser_id": self.bid,
        }
        self.proxysession.options(
            "https://api.interpreter.caiyunai.com/v1/user/jwt/generate",
            headers=headers,
            json=json_data,
        )
        self.jwt = self.proxysession.post(
            "https://api.interpreter.caiyunai.com/v1/user/jwt/generate",
            headers=headers,
            json=json_data,
        ).json()["jwt"]

        headers = {
            "authority": "api.interpreter.caiyunai.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "app-name": "xy",
            "cache-control": "no-cache",
            "device-id": "",
            "origin": "https://fanyi.caiyunapp.com",
            "os-type": "web",
            "os-version": "",
            "pragma": "no-cache",
            "referer": "https://fanyi.caiyunapp.com/",
            "sec-ch-ua": '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "t-authorization": self.jwt,
            "x-authorization": self.token,
        }

        json_data = {
            "source": content,
            "trans_type": self.srclang + "2" + self.tgtlang,
            "request_id": "web_fanyi",
            "media": "text",
            "os_type": "web",
            "dict": True,
            "cached": True,
            "replaced": True,
            "detect": True,
            "browser_id": self.bid,
        }
        self.proxysession.options(
            "https://api.interpreter.caiyunai.com/v1/translator",
            headers=headers,
            json=json_data,
        )
        response = self.proxysession.post(
            "https://api.interpreter.caiyunai.com/v1/translator",
            headers=headers,
            json=json_data,
        )
        try:
            return decrypt(response.json()["target"])
        except:
            raise Exception(response)
