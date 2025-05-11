import json
import hashlib
import hmac
import uuid
import datetime
import base64
from translator.basetranslator import basetrans
from language import Languages


class TS(basetrans):
    def langmap(self):
        return {Languages.TradChinese: "zh-tw"}

    def translate(self, query):
        self.checkempty(["Access_Key"])
        self.checkempty(["SECRET_KEY"])
        access_key_id = self.multiapikeycurrent["Access_Key"]
        access_key_secret = self.multiapikeycurrent["SECRET_KEY"]
        url = "http://mt.cn-hangzhou.aliyuncs.com/api/translate/web/general"
        req_body = {
            "Action": "Translate",
            "FormatType": "text",
            "SourceLanguage": self.srclang,
            "TargetLanguage": self.tgtlang,
            "SourceText": query,
            "Scene": "general",
        }
        req_body = json.dumps(req_body)
        date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        nonce = str(uuid.uuid4())
        md5 = hashlib.md5(req_body.encode("utf-8"))
        content_md5 = base64.b64encode(md5.digest()).decode("utf-8")
        stringToSign = "{method}\n{accept}\n{md5}\n{content_type}\n{date}\nx-acs-signature-method:HMAC-SHA1\nx-acs-signature-nonce:{nonce}\nx-acs-version:{version}\n{path}".format(
            method="POST",
            accept="application/json",
            md5=content_md5,
            content_type="application/json; charset=utf-8",
            date=date,
            nonce=nonce,
            version="2019-01-02",
            path="/api/translate/web/general",
        )
        key = access_key_secret.encode("utf-8")
        message = stringToSign.encode("utf-8")
        signed = hmac.new(key, message, digestmod=hashlib.sha1).digest()
        signature = base64.b64encode(signed).decode("utf-8")
        authorization = "acs {}:{}".format(access_key_id, signature)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Content-MD5": content_md5,
            "Date": date,
            "Host": "mt.cn-hangzhou.aliyuncs.com",
            "Authorization": authorization,
            "x-acs-signature-nonce": nonce,
            "x-acs-signature-method": "HMAC-SHA1",
            "x-acs-version": "2019-01-02",
        }
        request = self.proxysession.post(url, headers=headers, data=req_body)
        try:
            response = request.json()
            return response["Data"]["Translated"]
        except:
            raise Exception(request)
