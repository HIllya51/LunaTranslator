import urllib.request
import urllib.error
import json
import re
import os

os.chdir(os.path.abspath(os.path.dirname(__file__)))

url = "https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b10798"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        data = response.read().decode("utf-8")
        js = json.loads(data)
except urllib.error.HTTPError as e:
    print(f"HTTP 错误: {e.code} - {e.reason}")
    raise
except urllib.error.URLError as e:
    print(f"网络错误: {e.reason}")
    raise

jss = {}
jss["html_url"] = js["html_url"]
jss["tag_name"] = js["tag_name"]
jss["assets"] = []
for _ in js["assets"]:
    name: str = _["name"]
    maich1 = re.match(r"cudart-llama-bin-win-(.*?)-x64\.zip", name)
    maich2 = re.match(r"llama-.*?-bin-win-(.*?)-x64\.zip", name)
    if not maich1 and not maich2:
        continue
    __ = {}
    __["name"] = _["name"]
    __["size"] = _["size"]
    __["digest"] = _["digest"]
    __["browser_download_url"] = _["browser_download_url"]
    jss["assets"].append(__)

with open(
    "../LunaTranslator/defaultconfig/llama.cpp.version.json", "w", encoding="utf8"
) as ff:
    ff.write(json.dumps(jss, indent=4))
