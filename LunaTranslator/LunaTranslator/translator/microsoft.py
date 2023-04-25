 
from traceback import print_exc
import requests
from urllib.parse import quote
import re
import json  

from utils.config import globalconfig
from translator.basetranslator import basetrans
import time

import base64,datetime 
import json
import hashlib
import hmac,uuid
from datetime import datetime
from urllib.parse import quote
import json
from http.client import HTTPConnection
from urllib.parse import quote
import json
import requests

def translate_async(text, to_language, from_language=None,proxy=None): 
    _apiEndpoint = "api.cognitive.microsofttranslator.com";
    _apiVersion = "3.0";
    url = f'{_apiEndpoint}/translate?api-version={_apiVersion}&to={to_language}'
    if from_language is not None:
        url += f'&from={ from_language }'
    _privateKey =[
        0xa2, 0x29, 0x3a, 0x3d, 0xd0, 0xdd, 0x32, 0x73,
        0x97, 0x7a, 0x64, 0xdb, 0xc2, 0xf3, 0x27, 0xf5,
        0xd7, 0xbf, 0x87, 0xd9, 0x45, 0x9d, 0xf0, 0x5a,
        0x09, 0x66, 0xc6, 0x30, 0xc6, 0x6a, 0xaa, 0x84,
        0x9a, 0x41, 0xaa, 0x94, 0x3a, 0xa8, 0xd5, 0x1a,
        0x6e, 0x4d, 0xaa, 0xc9, 0xa3, 0x70, 0x12, 0x35,
        0xc7, 0xeb, 0x12, 0xf6, 0xe8, 0x23, 0x07, 0x9e,
        0x47, 0x10, 0x95, 0x91, 0x88, 0x55, 0xd8, 0x17
    ]
    headers = {
        'X-MT-Signature': get_signature(url,_privateKey),
        'Content-Type': 'application/json'
    }
    json_data = [{"Text": text}]
    response = requests.post(f'https://{url}', headers=headers, data=json.dumps(json_data).encode('utf-8'),proxies=proxy)

    response.raise_for_status()

    data_json = response.json()
    root = data_json[0]['translations'][0]['text']
    return root

def get_signature(url, private_key):
    guid = str(uuid.uuid4()).replace('-', '')
    escaped_url = quote(url, safe='')

    dateTime = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    bytes_str = f'MSTranslatorAndroidApp{escaped_url}{dateTime}{guid}'.lower().encode('utf-8')
     
    hash_ = hmac.new(bytes(private_key), bytes_str, hashlib.sha256).digest()

    signature = f'MSTranslatorAndroidApp::{base64.b64encode(hash_).decode()}::{dateTime}::{guid}'
    return signature

def try_get_expiration_date(element, expiration_date):
    token = element.get_string()
    span = token.as_span()
    index = span.index('.')
    last_index = span.last_index_of('.')
    
    if index != -1 and index < last_index:
        encoded_payload = token[index+1:last_index]
        payload = base64_url_decode(encoded_payload)
        
        document = json.loads(payload.decode('utf-8'))
        if 'exp' in document and isinstance(document['exp'], int):
            expiration_date = datetime.utcfromtimestamp(document['exp'])
            return True
    
    expiration_date = None
    return False

def base64_url_decode(text):
    padding = 3 - (len(text) + 3) % 4
    if padding > 0:
        text += '=' * padding

    return base64.b64decode(text.replace('-', '+').replace('_', '/'))

class TS(basetrans):
    def langmap(self):
        return {"zh":"zh-CN","cht":"zh-TW"}
    def translate(self,content): 
            
        return translate_async(content,self.tgtlang,self.srclang,self.proxy)
    