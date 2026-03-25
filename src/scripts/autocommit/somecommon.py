import subprocess
import os
import requests
from llmapis import *

os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


def get_original_git_show(commit_hash):
    # 使用 --no-color 确保输出不带转义字符
    # 使用 --no-pager 确保不进入分页模式
    result = subprocess.check_output(
        ["git", "--no-pager", "show", "--no-color", "--format=", commit_hash],
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    return result


def call_llm_api(prompt: str, api_key: str, api_url: str, model: str):

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional Git commit message generator assistant. You need to generate concise commit messages based on code changes.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "max_tokens": 300,
    }
    response = requests.post(api_url, headers=headers, json=data, timeout=30)
    try:
        result = response.json()
        message = result["choices"][0]["message"]["content"].strip()
        return message
    except:
        raise Exception(response.text)


def generate_commit_messages(diff_text: str):
    chinese_prompt = f"""Based on the Git diff provided, generate an English commit message. Do not describe overly specific code changes.

Git diff:
```
{diff_text}
```"""

    chinese_msg = call_llm_api(chinese_prompt, api_key, api_url, model)
    return chinese_msg
