import pytz

# import websocket
# 不知道为什么，curl不发送headers。回头再研究吧。
from network.client.winhttp.websocket import WebSocket
from datetime import datetime
import time
import re
import uuid, hashlib
from tts.basettsclass import TTSbase, SpeechParam, TTSResult

# https://github.com/rany2/edge-tts

BASE_URL = "speech.platform.bing.com/consumer/speech/synthesize/readaloud"
TRUSTED_CLIENT_TOKEN = "6A5AA1D4EAFF4E9FB37E23D68491D6F4"

WSS_URL = "wss://{}/edge/v1?TrustedClientToken={}".format(
    BASE_URL, TRUSTED_CLIENT_TOKEN
)
VOICE_LIST = "https://{}/voices/list?trustedclienttoken={}".format(
    BASE_URL, TRUSTED_CLIENT_TOKEN
)

CHROMIUM_FULL_VERSION = "130.0.2849.68"
CHROMIUM_MAJOR_VERSION = CHROMIUM_FULL_VERSION.split(".", maxsplit=1)[0]
SEC_MS_GEC_VERSION = "1-{}".format(CHROMIUM_FULL_VERSION)
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/{CHROMIUM_MAJOR_VERSION}.0.0.0 Safari/537.36"
    " Edg/{CHROMIUM_MAJOR_VERSION}.0.0.0".format(
        CHROMIUM_MAJOR_VERSION=CHROMIUM_MAJOR_VERSION
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
WSS_HEADERS = {
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Origin": "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold",
}
WSS_HEADERS.update(BASE_HEADERS)
VOICE_HEADERS = {
    "Authority": "speech.platform.bing.com",
    "Sec-CH-UA": '" Not;A Brand";v="99", "Microsoft Edge";v="{CHROMIUM_MAJOR_VERSION}", "Chromium";v="{CHROMIUM_MAJOR_VERSION}"'.format(
        CHROMIUM_MAJOR_VERSION=CHROMIUM_MAJOR_VERSION
    ),
    "Sec-CH-UA-Mobile": "?0",
    "Accept": "*/*",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
}
VOICE_HEADERS.update(BASE_HEADERS)

WIN_EPOCH = 11644473600
S_TO_NS = 1e9


class DRM:
    """
    Class to handle DRM operations with clock skew correction.
    """

    clock_skew_seconds: float = 0.0

    @staticmethod
    def adj_clock_skew_seconds(skew_seconds: float) -> None:
        DRM.clock_skew_seconds += skew_seconds

    @staticmethod
    def get_unix_timestamp() -> float:
        return datetime.now(pytz.utc).timestamp() + DRM.clock_skew_seconds

    @staticmethod
    def parse_rfc2616_date(date: str):
        try:
            return (
                datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
                .replace(tzinfo=pytz.utc)
                .timestamp()
            )
        except ValueError:
            return None

    @staticmethod
    def generate_sec_ms_gec() -> str:
        # Get the current timestamp in Windows file time format with clock skew correction
        ticks = DRM.get_unix_timestamp()

        # Switch to Windows file time epoch (1601-01-01 00:00:00 UTC)
        ticks += WIN_EPOCH

        # Round down to the nearest 5 minutes (300 seconds)
        ticks -= ticks % 300

        # Convert the ticks to 100-nanosecond intervals (Windows file time format)
        ticks *= S_TO_NS / 100

        # Create the string to hash by concatenating the ticks and the trusted client token
        str_to_hash = "{:.0f}{}".format(ticks, TRUSTED_CLIENT_TOKEN)

        # Compute the SHA256 hash and return the uppercased hex digest
        return hashlib.sha256(str_to_hash.encode("ascii")).hexdigest().upper()


class TTS(TTSbase):

    def getvoicelist(self):
        alllist = self.proxysession.get(
            "{}&Sec-MS-GEC={}&Sec-MS-GEC-Version={}".format(
                VOICE_LIST, DRM.generate_sec_ms_gec(), SEC_MS_GEC_VERSION
            ),
            headers=VOICE_HEADERS,
        ).json()
        return [_["ShortName"] for _ in alllist], [_["FriendlyName"] for _ in alllist]

    def speak(self, content, voice, param: SpeechParam):
        return transferMsTTSData(self.createSSML(content, voice, param), self.proxy)


# Fix the time to match Americanisms
def hr_cr(hr):
    corrected = (hr - 1) % 24
    return str(corrected)


# Add zeros in the right places i.e 22:1:5 -> 22:01:05
def fr(input_string):
    corr = ""
    i = 2 - len(input_string)
    while i > 0:
        corr += "0"
        i -= 1
    return corr + input_string


# Generate X-Timestamp all correctly formatted
def getXTime():
    now = datetime.now()
    return (
        fr(str(now.year))
        + "-"
        + fr(str(now.month))
        + "-"
        + fr(str(now.day))
        + "T"
        + fr(hr_cr(int(now.hour)))
        + ":"
        + fr(str(now.minute))
        + ":"
        + fr(str(now.second))
        + "."
        + str(now.microsecond)[:3]
        + "Z"
    )


def date_to_string() -> str:
    """
    Return Javascript-style date string.

    Returns:
        str: Javascript-style date string.
    """
    # %Z is not what we want, but it's the only way to get the timezone
    # without having to use a library. We'll just use UTC and hope for the best.
    # For example, right now %Z would return EEST when we need it to return
    # Eastern European Summer Time.
    return time.strftime(
        "%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)", time.gmtime()
    )


def ssml_headers_plus_data(request_id: str, timestamp: str, ssml: str) -> str:
    """
    Returns the headers and data to be used in the request.

    Returns:
        str: The headers and data to be used in the request.
    """

    return (
        "X-RequestId:{}\r\n".format(request_id)
        + "Content-Type:application/ssml+xml\r\n"
        "X-Timestamp:{}Z\r\n".format(timestamp)
        + "Path:ssml\r\n\r\n"  # This is not a mistake, Microsoft Edge bug.
        "{}".format(ssml)
    )


def connect_id() -> str:
    """
    Returns a UUID without dashes.

    Returns:
        str: A UUID without dashes.
    """
    return str(uuid.uuid4()).replace("-", "")


def transferMsTTSData(ssml, proxy_: "dict[str, str]"):

    proxy = proxy_["https"]
    if proxy:
        ip, port = proxy.split(":")
    else:
        ip = port = None
    ws = WebSocket()
    ws.connect(
        "{}&Sec-MS-GEC={}&Sec-MS-GEC-Version={}&ConnectionId={}".format(
            WSS_URL, DRM.generate_sec_ms_gec(), SEC_MS_GEC_VERSION, connect_id()
        ),
        header=WSS_HEADERS,
        http_proxy_host=ip,
        http_proxy_port=port,
    )

    date = date_to_string()

    ws.send(
        "X-Timestamp:{}\r\n".format(date)
        + "Content-Type:application/json; charset=utf-8\r\n"
        "Path:speech.config\r\n\r\n"
        '{"context":{"synthesis":{"audio":{"metadataoptions":{'
        '"sentenceBoundaryEnabled":false,"wordBoundaryEnabled":true},'
        '"outputFormat":"audio-24khz-48kbitrate-mono-mp3"'
        "}}}}\r\n"
    )

    ws.send(ssml_headers_plus_data(connect_id(), date, ssml))

    end_resp_pat = re.compile("Path:turn.end")

    def __():
        while True:
            response = ws.recv()
            if response[:2] == b"\x03\xef":
                raise Exception(response[2:].decode())
            # print(type(response),"++++++++++++")
            # Make sure the message isn't telling us to stop
            if re.search(end_resp_pat, str(response)) == None:
                # Check if our response is text data or the audio bytes
                if type(response) == type(bytes()):
                    # Extract binary data
                    try:
                        needle = b"Path:audio\r\n"
                        idx = response.find(needle)
                        if idx == -1:
                            raise Exception()
                        start_ind = idx + len(needle)
                        yield response[start_ind:]
                    except:
                        yield response
            else:
                break
        ws.close()

    return TTSResult(__(), type="audio/mpeg")
