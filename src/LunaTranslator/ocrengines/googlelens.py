from ocrengines.baseocrclass import baseocr
import re, time


class OCR(baseocr):

    def ocr(self, imagebinary):
        # https://github.com/AuroraWright/owocr/blob/master/owocr/ocr.py

        regex = re.compile(r">AF_initDataCallback\(({key: 'ds:1'.*?)\);</script>")

        timestamp = int(time.time() * 1000)
        url = f"https://lens.google.com/v3/upload?stcs={timestamp}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3771) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.144 Mobile Safari/537.36",
        }
        cookies = {"SOCS": "CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg"}

        files = {"encoded_image": ("screenshot.png", imagebinary, "image/png")}
        res = self.proxysession.post(
            url, files=files, headers=headers, cookies=cookies, timeout=20
        )
        match = regex.search(res.text)
        if match == None:
            return
        sideChannel = "sideChannel"
        null = None
        key = "key"
        # hash="hash"
        data = "data"
        true = True
        false = False
        lens_object = eval(match.group(1))
        if "errorHasStatus" in lens_object:
            raise Exception(False, "Unknown Lens error!")

        res = ""
        text = lens_object["data"][3][4][0]
        if len(text) == 0:
            return
        return text[0]
