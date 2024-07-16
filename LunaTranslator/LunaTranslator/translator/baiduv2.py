import requests
import re
from translator.basetranslator import basetrans
import time, urllib
import math


def n(t, e):
    n = 0
    while n < len(e) - 2:
        r = e[n + 2]
        if "a" <= r:
            r = ord(r) - 87
        else:
            r = int(r)
        if "+" == e[n + 1]:
            r = t >> r
        else:
            r = t << r
        if "+" == e[n]:
            t = t + r & 4294967295

        else:
            t = t ^ r
        n += 3
    return t


def b(t, gtk):
    r = gtk

    a = len(t)
    if a > 30:
        t = t[:10] + t[math.floor(a / 2) - 5 : math.floor(a / 2) - 5 + 10] + t[-10:]

    h = r.split(".")
    f = int(h[0])

    m = int(h[1])
    g = []
    v = 0
    while v < len(t):
        _ = ord(t[v])
        if _ < 128:
            g.append(_)
        else:
            if _ < 2048:
                g.append(_ >> 6 | 192)
            else:
                if (
                    55296 == (64512 & _)
                    and v + 1 < len(t)
                    and 56320 == (64512 & t[v + 1])
                ):
                    v += 1
                    _ = 65536 + ((1023 & _) << 10 + (1023 & ord(t[v])))
                    g.append(_ >> 18 | 240)
                    g.append(_ >> 12 & 63 | 128)
                else:
                    g.append(_ >> 12 | 224)
                    g.append(_ >> 6 & 63 | 128)
                    g.append(63 & _ | 128)
        v += 1
    b = f
    w = "+-a^+6"
    k = "+-3^+b+-f"
    x = 0
    while x < len(g):
        b += g[x]
        b = n(b, w)
        x += 1
    b = n(b, k)
    b ^= m
    if b < 0:
        b = 2147483648 + (2147483647 & b)
    b %= 1e6
    b = int(b)
    return str(b) + "." + str(b ^ f)


class BaiduTranslate:
    def __init__(self):
        self.headers = {
            "Host": "fanyi.baidu.com",
            "Origin": "https://fanyi.baidu.com",
            "Cookie": 'BAIDUID=2075799560CB805468E46C062291C3CA:FG=1; PSTM=1710310886; BIDUPSID=B15467B23371BD127587BB726566C72B; BDUSS=mVBN2kzSFZ4OERFQ3hod3BXamk2bjl6YkhUT35jZnI5UERTaH5nS3p6MEgwU0JtRVFBQUFBJCQAAAAAAAAAAAEAAAD1-B2zAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdE-WUHRPllU; BDUSS_BFESS=mVBN2kzSFZ4OERFQ3hod3BXamk2bjl6YkhUT35jZnI5UERTaH5nS3p6MEgwU0JtRVFBQUFBJCQAAAAAAAAAAAEAAAD1-B2zAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdE-WUHRPllU; newlogin=1; H_PS_PSSID=40304_40080_40463; H_WISE_SIDS=40304_40080_40463; BAIDUID_BFESS=2075799560CB805468E46C062291C3CA:FG=1; ZFY=R542yFk7iD7:B0KVN:AELgNejr4Bl5IeQAioFd9VbCgkY:C; H_WISE_SIDS_BFESS=40304_40080_40463; smallFlowVersion=old; APPGUIDE_10_7_2=1; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; BDRCVFR[r5ISJbddYbD]=3yOp2bF5zzbmhF1Tv38mvqV; BA_HECTOR=8ka58h2g21ag242ka185840g601h1q1j2rc2n1s; PSINO=6; delPer=0; BCLID=6565329525091269733; BCLID_BFESS=6565329525091269733; BDSFRCVID=xnuOJeC62w-31-ctaErjUmHOVg3SOxnTH6aoyisApyjRGOU0mrB4EG0PaU8g0KubrqyqogKK3gOTH4PF_2uxOjjg8UtVJeC6EG0Ptf8g0f5; BDSFRCVID_BFESS=xnuOJeC62w-31-ctaErjUmHOVg3SOxnTH6aoyisApyjRGOU0mrB4EG0PaU8g0KubrqyqogKK3gOTH4PF_2uxOjjg8UtVJeC6EG0Ptf8g0f5; H_BDCLCKID_SF=tJk8oDPbJK03fP36q4jqMJtJ5eT22jn42Jb9aJ5y-J7nhnnTDPbM-fLXDnoLBURp523ion3vQpbZql5EbJjb2jkbWxTEJp5lLIn9Kl0MLP-WoJklQfrD3h3QXfnMBMPe52OnaIbx3fAKftnOM46JehL3346-35543bRTLnLy5KJYMDFRD5uhDjObDaRK5b30bD5JX6rD5RT5j-Kk-PI32-C0XP6-35KHb-Deo66JbnjpqRcahf7c34by0PnO2q37JD6yXRTb04JBjxojXp_2hJDYj-oxJpOKQRbMopvaKtoaJtjvbURvDP-g3-AJQU5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-j5JIE3-oJqCKMbDL43j; H_BDCLCKID_SF_BFESS=tJk8oDPbJK03fP36q4jqMJtJ5eT22jn42Jb9aJ5y-J7nhnnTDPbM-fLXDnoLBURp523ion3vQpbZql5EbJjb2jkbWxTEJp5lLIn9Kl0MLP-WoJklQfrD3h3QXfnMBMPe52OnaIbx3fAKftnOM46JehL3346-35543bRTLnLy5KJYMDFRD5uhDjObDaRK5b30bD5JX6rD5RT5j-Kk-PI32-C0XP6-35KHb-Deo66JbnjpqRcahf7c34by0PnO2q37JD6yXRTb04JBjxojXp_2hJDYj-oxJpOKQRbMopvaKtoaJtjvbURvDP-g3-AJQU5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-j5JIE3-oJqCKMbDL43j; RT="z=1&dm=baidu.com&si=8b8aca4f-f75c-474e-94aa-7edaa05d914f&ss=lvizc8dk&sl=3&tt=51h&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=o2bb&ul=o3jn&hd=o3nm"; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; ab_sr=1.0.1_OGY1YmU0NDFmMmExZjgxZjc1YzYxYmYxNDcxN2E1YWUxMTQ5YzMyYTA4ZGI0MzU2ZDRkY2MzNTkwNGQ3MjBiNjc5ZDAyMGQ3ZTYxYTg5ZGFhNDQyYzliNTU4MmU5ZjM1YmRhNDQ5NDhlZGJiYjc0NzkwZTdlYzI1MjM0ZTg0ZGQ5MDVlMWU1ZjNkZGU3NzgzZTc0OTA4ZjRlNzRjY2Q5YzhiMjlmYjVhYTMxNDMzMDViM2E2NmVlZWE3YTdjZTUx',
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "https://fanyi.baidu.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        }
        self.session = requests.Session()
        self.index_url = "https://fanyi.baidu.com/"
        self.url = "https://fanyi.baidu.com/v2transapi?from=zh&to=en"

    def get_sign(self, input_key):
        sign = b(input_key, self.gtk)
        return sign

    def key_parameter(self, proxy):
        response = self.session.get(
            self.index_url, headers=self.headers, proxies=proxy
        ).text
        self.token = re.findall("token: '(.*?)',", response)[0]
        self.gtk = re.findall('window.gtk = "(.*?)";', response)[0]

    def translate(self, input_key, src, tgt, proxies):
        data = {
            "from": src,
            "to": tgt,
            "query": input_key,
            "simple_means_flag": "3",
            "sign": self.get_sign(input_key),
            "token": self.token,
            "domain": "common",
            "ts": str(int(time.time() * 1000)),
        }
        response = self.session.post(
            url=self.url, headers=self.headers, data=data, proxies=proxies
        )

        translation_data = response.json()
        try:
            translation = translation_data["trans_result"]["data"][0]["dst"]
            return translation
        except:
            raise Exception(translation_data)


class TS(basetrans):
    def langmap(self):
        return {
            "es": "spa",
            "ko": "kor",
            "fr": "fra",
            "ja": "jp",
            "cht": "cht",
            "vi": "vie",
            "uk": "ukr",
            "ar": "ara",
        }

    def inittranslator(self):

        self.engine = BaiduTranslate()
        self.engine.key_parameter(self.proxy)

    def translate(self, query):
        return self.engine.translate(
            query, self.srclang, self.tgtlang, proxies=self.proxy
        )
