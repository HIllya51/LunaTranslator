from ocrengines.baseocrclass import baseocr
import re
import time
import random

class OCR(baseocr):
    user_agents = [
        "Mozilla/5.0 (Fuchsia) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 CrKey/1.56.500000",
        "Mozilla/5.0 (Linux; Android) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.109 Safari/537.36 CrKey/1.54.248666",
        "Mozilla/5.0 (Linux; Android 9; AFTSS) AppleWebKit/537.36 (KHTML, like Gecko) Silk/112.5.1 like Chrome/112.0.5615.213 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 7.1.2; AFTMM) AppleWebKit/537.36 (KHTML, like Gecko) Silk/112.5.1 like Chrome/112.0.5615.213 Safari/537.36",
        "Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/4.0 Chrome/76.0.3809.146 TV Safari/537.36",
        "Mozilla/5.0 (Linux; Tizen 2.3; SmartHub; SMART-TV; SmartTV; U; Maple2012) waipu/2023.6.11-2494 (TV; Samsung; 17_KANTM_UHD; waipu; Tizen 3.0)"
    ]

    def ocr(self, imagebinary):
        regex = re.compile(r">AF_initDataCallback\(({key: 'ds:1'.*?)\);</script>")
        timestamp = int(time.time() * 1000)
        url = f"https://lens.google.com/v3/upload?stcs={timestamp}"
        headers = {
            "User-Agent": random.choice(self.user_agents),  # Rotate user-agents
        }
        files = {"encoded_image": ("screenshot.png", imagebinary, "image/png")}
        res = self.proxysession.post(url, files=files, headers=headers)
        match = regex.search(res.text)
        if not match:
            return
        sideChannel = "sideChannel"
        null = None
        key = "key"
        data = "data"
        true = True
        false = False
        lens_object = eval(match.group(1))
        if "errorHasStatus" in lens_object:
            raise Exception(False, "Unknown Lens error!")
        
        text = lens_object["data"][3][4][0]
        
        # Write to a log text file in utf-8 with signature
        if text:
            text_list = list(text[0]) if text else []
            with open("log.txt", "a", encoding="utf-8-sig") as file:
                file.write("\n".join(text_list) + "\n")
        return text_list if text else None
