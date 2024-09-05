from translator.basetranslator import basetrans
import json
from myutils.utils import createenglishlangmap
from datetime import datetime
import hashlib, sys, hmac, time, json


def sign_tc3(secret_key, date, service, str2sign):
    def _hmac_sha256(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256)

    def _get_signature_key(key, date, service):
        k_date = _hmac_sha256(("TC3" + key).encode("utf-8"), date)
        k_service = _hmac_sha256(k_date.digest(), service)
        k_signing = _hmac_sha256(k_service.digest(), "tc3_request")
        return k_signing.digest()

    signing_key = _get_signature_key(secret_key, date, service)
    signature = _hmac_sha256(signing_key, str2sign).hexdigest()
    return signature


def _get_tc3_signature(
    header, method, canonical_uri, payload, secret_key, date, service, options=None
):
    options = options or {}
    canonical_querystring = ""

    if sys.version_info[0] == 3 and isinstance(payload, type("")):
        payload = payload.encode("utf8")

    payload_hash = hashlib.sha256(payload).hexdigest()

    canonical_headers = "content-type:%s\nhost:%s\n" % (
        header["Content-Type"],
        header["Host"],
    )
    signed_headers = "content-type;host"
    canonical_request = "%s\n%s\n%s\n%s\n%s\n%s" % (
        method,
        canonical_uri,
        canonical_querystring,
        canonical_headers,
        signed_headers,
        payload_hash,
    )

    algorithm = "TC3-HMAC-SHA256"
    credential_scope = date + "/" + service + "/tc3_request"
    if sys.version_info[0] == 3:
        canonical_request = canonical_request.encode("utf8")
    digest = hashlib.sha256(canonical_request).hexdigest()
    string2sign = "%s\n%s\n%s\n%s" % (
        algorithm,
        header["X-TC-Timestamp"],
        credential_scope,
        digest,
    )

    return sign_tc3(secret_key, date, service, string2sign)


def _build_req_with_tc3_signature(key, _id, action, params, options=None):
    header = {}
    header["Content-Type"] = "application/json"

    endpoint = "hunyuan.tencentcloudapi.com"
    timestamp = int(time.time())
    header["Host"] = endpoint
    header["X-TC-Action"] = action[0].upper() + action[1:]
    header["X-TC-RequestClient"] = "SDK_PYTHON_3.0.1193"
    header["X-TC-Timestamp"] = str(timestamp)
    header["X-TC-Version"] = "2023-09-01"
    data = json.dumps(params).encode("utf8")

    service = "hunyuan"
    date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
    signature = _get_tc3_signature(
        header, "POST", "/", data, key, date, service, options
    )

    auth = (
        "TC3-HMAC-SHA256 Credential=%s/%s/%s/tc3_request, SignedHeaders=content-type;host, Signature=%s"
        % (_id, date, service, signature)
    )
    header["Authorization"] = auth
    return header


class TS(basetrans):

    def langmap(self):
        return createenglishlangmap()

    def __init__(self, typename):
        self.context = []
        super().__init__(typename)

    def translate(self, query):
        self.checkempty(["secret_id", "secret_key"])
        self.contextnum = int(self.config["context_num"])
        query = self._gptlike_createquery(
            query, "use_user_user_prompt", "user_user_prompt"
        )
        sysprompt = self._gptlike_createsys("use_user_prompt", "user_prompt")
        message = [{"Role": "system", "Content": sysprompt}]

        for _i in range(min(len(self.context) // 2, self.contextnum)):
            i = (
                len(self.context) // 2
                - min(len(self.context) // 2, self.contextnum)
                + _i
            )
            message.append(self.context[i * 2])
            message.append(self.context[i * 2 + 1])
        message.append({"Role": "user", "Content": query})
        usingstream = self.config["usingstream"]
        json_data = {
            "Model": self.config["model"],
            "Messages": message,
            "Stream": usingstream,
            "TopP": self.config["top_p"],
            "Temperature": self.config["Temperature"],
        }
        headers = _build_req_with_tc3_signature(
            self.multiapikeycurrent["secret_key"],
            self.multiapikeycurrent["secret_id"],
            "ChatCompletions",
            json_data,
        )
        response = self.proxysession.post(
            "https://hunyuan.tencentcloudapi.com/",
            headers=headers,
            data=json.dumps(json_data),
            stream=usingstream,
        )

        if usingstream:
            message = ""
            for i in response.iter_lines():

                if not i:
                    continue
                i = i.decode("utf8")[6:]
                try:
                    mes = json.loads(i)["Choices"][0]["Delta"]["Content"]
                except:
                    raise Exception(i)
                yield mes
                message += mes

        else:
            try:
                message = response.json()["Response"]["Choices"][0]["Message"][
                    "Content"
                ]
            except:
                raise Exception(response.text)
            yield message
        self.context.append({"Role": "user", "Content": query})
        self.context.append({"Role": "assistant", "Content": message})
