import json
import os
from turtle import pos 
 
with open('./files/config.json','r',encoding='utf-8') as ff:
    globalconfig=json.load(ff)
              

with open('./files/postprocessconfig.json','r',encoding='utf-8') as ff:
    postprocessconfig=json.load(ff)


with open('./files/noundictconfig.json','r',encoding='utf-8') as ff:
    noundictconfig=json.load(ff)