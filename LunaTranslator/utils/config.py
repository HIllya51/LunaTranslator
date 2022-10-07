import json
from math import fabs
import os
from turtle import pos 
 
with open('./files/config.json','r',encoding='utf-8') as ff:
    globalconfig=json.load(ff)
              

with open('./files/postprocessconfig.json','r',encoding='utf-8') as ff:
    postprocessconfig=json.load(ff)


with open('./files/noundictconfig.json','r',encoding='utf-8') as ff:
    noundictconfig=json.load(ff)

if os.path.exists('./files/transerrorfixdictconfig.json'):
    with open('./files/transerrorfixdictconfig.json','r',encoding='utf-8') as ff:
        transerrorfixdictconfig=json.load(ff)
else:
    transerrorfixdictconfig={"use":False,"dict":{}}


if 'fanjian' not in globalconfig:
    globalconfig['fanjian']=0


if 'rotation' not in globalconfig:
    globalconfig['rotation']=0



if 'srclang' not in globalconfig:
    globalconfig['srclang']=0

#0 ja  1 eng