import json
import os 

fname=os.path.join('./files/config.json')

with open(fname,'r',encoding='utf-8') as ff:
    config1=json.load(ff)
            
         
             
globalconfig=config1
#print(globalconfig)