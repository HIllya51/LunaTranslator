import hmac, base64, re
import uuid, time
from translator.basetranslator import basetrans
from language import Languages


class TS(basetrans):
    def langmap(self):
        return {Languages.Chinese: "zh-CN", Languages.TradChinese: "zh-TW"}

    def init(self):
        headers = {
            "authority": "papago.naver.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "zh-CN,zh;q=0.9",
            "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }
        host_html = self.proxysession.get(
            "https://papago.naver.com/", headers=headers
        ).text
        url_path = re.compile("/main.(.*?).chunk.js").search(host_html).group()
        self.language_url = "".join(["https://papago.naver.com", url_path])
        lang_html = self.proxysession.get(self.language_url, headers=headers).text
        self.auth_key = re.search(r'"PPG "(.*)"(.*?)"\).toString', lang_html).groups()[
            1
        ]
        # Authorization: "PPG " + t + ":" + p.a.HmacMD5(t + "\n" + e.split("?")[0] + "\n" + n, "v1.8.4_bbf86e0446").toString(p.a.enc.Base64),

        self.uuid = uuid.uuid4().__str__()

    def get_auth(self, url, auth_key, device_id, time_stamp):
        auth = hmac.new(
            key=auth_key.encode(),
            msg="{}\n{}\n{}".format(device_id, url, time_stamp).encode(),
            digestmod="md5",
        ).digest()
        return "PPG {}:{}".format(device_id, base64.b64encode(auth).decode())

    def translate(self, content):
        tm = str(int(time.time() * 1000))
        headers = {
            "authority": "papago.naver.com",
            "accept": "application/json",
            "accept-language": "zh-CN",
            "authorization": self.get_auth(
                "https://papago.naver.com/apis/n2mt/translate",
                self.auth_key,
                self.uuid,
                tm,
            ),
            "device-type": "pc",
            "origin": "https://papago.naver.com",
            "referer": "https://papago.naver.com/",
            "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "timestamp": tm,
            "x-apigw-partnerid": "papago",
        }

        data = {
            "deviceId": self.uuid,
            "locale": self.tgtlang,
            "dict": "true",
            "dictDisplay": "30",
            "honorific": "false",
            "instant": "false",
            "paging": "false",
            "source": self.srclang,
            "target": self.tgtlang,
            "text": content,
        }

        r = self.proxysession.post(
            "https://papago.naver.com/apis/n2mt/translate", headers=headers, data=data
        )

        data = r.json()
        try:
            return data["translatedText"]
        except:
            raise Exception(data)
