 
from utils.config import globalconfig
import time
from urllib.parse import quote 
from translator.basetranslator import basetrans
import random
import urllib ,requests,json
API_URL = "https://www2.deepl.com/jsonrpc"

MAGIC_NUMBER = int("CAFEBABE", 16)
 
SUPPORTED_FORMALITY_TONES = ["formal", "informal"]
  

def read_file_lines(path):
    with open(path, "r") as file:
        return "\n".join(file.readlines())

from traceback import print_exc
headers = {
    "accept": "*/*",
    "accept-language": "en-US;q=0.8,en;q=0.7",
    "authority": "www2.deepl.com",
    "content-type": "application/json",
    "origin": "https://www.deepl.com",
    "referer": "https://www.deepl.com/translator",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": (
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/83.0.4103.97 Mobile Safari/537.36"
    ),
}
def extract_translated_sentences(json_response):
    translations = json_response["result"]["translations"]
    translated_sentences = [
        translation["beams"][0]["postprocessed_sentence"]
        for translation in translations
    ]
    return translated_sentences


def extract_split_sentences(json_response):
    return json_response["result"]["splitted_texts"][0]

def generate_split_sentences_request_data(text, identifier=MAGIC_NUMBER, **kwargs):
    return {
        "jsonrpc": "2.0",
        "method": "LMT_split_into_sentences",
        "params": {
            "texts": [text],
            "lang": {"lang_user_selected": "auto", "user_preferred_langs": []},
        },
        "id": identifier,
    }


def generate_jobs(sentences, beams=1):
    jobs = []
    for idx, sentence in enumerate(sentences):
        job = {
            "kind": "default",
            "raw_en_sentence": sentence,
            "raw_en_context_before": sentences[:idx],
            "raw_en_context_after": [sentences[idx + 1]]
            if idx + 1 < len(sentences)
            else [],
            "preferred_num_beams": beams,
        }
        jobs.append(job)
    return jobs

import time
from random import randrange


def calculate_valid_timestamp(timestamp, i_count):
    try:
        return timestamp + (i_count - timestamp % i_count)
    except ZeroDivisionError:
        return timestamp


def generate_timestamp(sentences):
    now = int(time.time() * 1000)
    i_count = 1
    for sentence in sentences:
        i_count += sentence.count("i")

    return calculate_valid_timestamp(now, i_count)


def generate_id():
    return randrange(1_000_000, 100_000_000)

def generate_common_job_params(formality_tone):
    if not formality_tone:
        return {}
    if formality_tone not in SUPPORTED_FORMALITY_TONES:
        raise ValueError(f"Formality tone '{formality_tone}' not supported.")
    return {"formality": formality_tone}


def generate_translation_request_data(
    source_language,
    target_language,
    sentences,
    identifier=MAGIC_NUMBER,
    alternatives=1,
    formality_tone=None,
):
    return {
        "jsonrpc": "2.0",
        "method": "LMT_handle_jobs",
        "params": {
            "jobs": generate_jobs(sentences, beams=alternatives),
            "lang": {
                "user_preferred_langs": [target_language, source_language],
                "source_lang_computed": source_language,
                "target_lang": target_language,
            },
            "priority": 1,
            "commonJobParams": generate_common_job_params(formality_tone),
            "timestamp": generate_timestamp(sentences),
        },
        "id": identifier,
    }

def split_into_sentences(text, **kwargs):
    data = generate_split_sentences_request_data(text, **kwargs)
    response = requests.post(API_URL, data=json.dumps(data), headers=headers)
    response.raise_for_status()

    json_response = response.json()
    sentences = extract_split_sentences(json_response)

    return sentences

def request_translation(source_language, target_language, text, **kwargs):
    sentences = split_into_sentences(text, **kwargs)
    data = generate_translation_request_data(
        source_language, target_language, sentences, **kwargs
    )
    response = requests.post(API_URL, data=json.dumps(data), headers=headers)
    return response


def translate(source_language, target_language, text, **kwargs): 

    response = request_translation(source_language, target_language, text, **kwargs)
    response.raise_for_status()

    json_response = response.json()
    translated_sentences = extract_translated_sentences(json_response)
    translated_text = " ".join(translated_sentences)

    return translated_text
from utils import somedef

class TS(basetrans):
    def langmap(self):
        x={_:_.upper() for _ in somedef.language_list_translator_inner}
        x.pop('cht')
        return  x
    def translate(self,content): 
            return translate(self.srclang, self.tgtlang, content)
            return self.engine.deepl_api(content,self.srclang,self.tgtlang)
         
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')