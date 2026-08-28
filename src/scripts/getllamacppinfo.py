import requests, re, json
import os
from tqdm import tqdm

os.chdir(os.path.dirname(__file__))
js = requests.get(
    "https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b10679"
).json()

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
