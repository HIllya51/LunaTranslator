import requests, re, json
import os
from tqdm import tqdm

os.chdir(os.path.dirname(__file__))
res = [
    {
        "series": "SakuraLLM",
        "lang": "ja->zh",
        "repos": [
            {"repo": "Sakura-14B-Qwen3-v1.5-GGUF"},
            {"repo": "GalTransl-v4-4B-2512"},
            {"repo": "Sakura-GalTransl-14B-v3.8"},
            {"repo": "Sakura-GalTransl-7B-v3.7"},
            {"repo": "Sakura-7B-Qwen2.5-v1.0-GGUF"},
            {"repo": "Sakura-32B-Qwen2beta-v0.10pre1-GGUF"},
        ],
    },
    {
        "series": "Shisa.AI",
        "account": "shisa-ai",
        "lang": "ja<->en",
        "repos": [
            {"account": "mradermacher", "repo": "shisa-v2.1-qwen3-8b-i1-GGUF"},
            {"account": "mradermacher", "repo": "shisa-v2-mistral-nemo-12b-GGUF"},
        ],
    },
    {
        "series": "TranslateGemma",
        "account": "google",
        "repos": [
            {"account": "bullerwins", "repo": "translategemma-4b-it-GGUF"},
            {"account": "bullerwins", "repo": "translategemma-12b-it-GGUF"},
            {"account": "bullerwins", "repo": "translategemma-27b-it-GGUF"},
        ],
    },
]
import time


def getNtimes(lk: str):
    _ = 1
    while True:
        try:
            return requests.get(lk)
        except requests.exceptions.RequestException:
            print(_, lk)
            time.sleep(min(5, _))
            _ += 1


def headNtimes(lk: str):
    _ = 1
    while True:
        try:
            return requests.head(lk, allow_redirects=True)
        except requests.exceptions.RequestException:
            print(_, lk)
            time.sleep(min(5, _))
            _ += 1


base = "huggingface.co"  # "hf-mirror.com"  #

for line in tqdm(res, position=0):
    for repo in tqdm(line["repos"], position=1, leave=False):
        account = line.get("account", line["series"])
        repoaccount = repo.get("account", account)
        lk = f"https://{base}/{repoaccount}/{repo['repo']}/tree/main"
        t = getNtimes(lk).text
        try:
            t = re.search(
                r'<ul class="mb-8 rounded-b-lg border border-t-0 dark:border-gray-800 dark:bg-gray-900">([\s\S]*?)</ul>',
                t,
            ).groups()[0]
        except:
            print(lk)
            raise Exception()
        t = re.findall(
            r'<li class="grid-cols-24 relative grid h-10 place-content-center gap-x-3 border-t px-3 dark:border-gray-800">([\s\S]*?)</li>',
            t,
        )
        ls = []
        for l in tqdm(t, position=2, leave=False):
            m = re.search(
                r'<span class="truncate group-hover:underline">(.*?)</span>', l
            ).groups()[0]
            if not m.lower().endswith("gguf"):
                continue
            tm = re.search(r'<time datetime="(.*?)"', l).groups()[0]
            # sz = re.search(
            #     r'<span class="truncate max-sm:text-xs">(.*?)</span>', l
            # ).groups()[0]
            sz = headNtimes(
                f"https://{base}/{repoaccount}/{repo['repo']}/resolve/main/{m}"
            ).headers["content-length"]
            sz = int(sz)
            internal = getNtimes(
                f"https://{base}/{repoaccount}/{repo['repo']}/blob/main/{m}"
            ).text
            sha = re.search(r'<dd class="truncate">(.*?)</dd>', internal).groups()[0]
            ls.append({"file": m, "size": sz, "timestamp": tm, "sha256": sha})
        repo["models"] = ls

with open(
    "../LunaTranslator/defaultconfig/llm_model_list.json", "w", encoding="utf8"
) as ff:
    ff.write(json.dumps(res, indent=4))
