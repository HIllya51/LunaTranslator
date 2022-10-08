import json 
import os 
from utils.defaultconfig import *

def tryreadconfig(path):
    if os.path.exists(path):
        with open(path,'r',encoding='utf-8') as ff:
            x=json.load(ff)
    else:
        x={}
    return x 
globalconfig=tryreadconfig('./files/config.json')
postprocessconfig=tryreadconfig('./files/postprocessconfig.json')
noundictconfig=tryreadconfig('./files/noundictconfig.json')
transerrorfixdictconfig=tryreadconfig('./files/transerrorfixdictconfig.json')
 
 


def syncconfig(config,default):
    for key in default:
        if key not in config:
            config[key]=default[key]
        if type(default[key])==dict:
            syncconfig(config[key],default[key])
    
        
syncconfig(transerrorfixdictconfig,defaulterrorfix)
syncconfig(postprocessconfig,defaultpost)
syncconfig(noundictconfig,defaultnoun)
syncconfig(globalconfig,defaultglobalconfig)
 
#0 ja  1 eng