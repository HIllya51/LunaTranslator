import json 
import os 
from utils.defaultconfig import *

def tryreadconfig(path):
    if os.path.exists(os.path.join('./userconfig/',path)):
        path=os.path.join('./userconfig/',path)
        with open(path,'r',encoding='utf-8') as ff:
            x=json.load(ff)
    elif os.path.exists(os.path.join('./files/',path)):
        path=os.path.join('./files/',path)
        with open(path,'r',encoding='utf-8') as ff:
            x=json.load(ff)
    else:
        x={}
    return x 

globalconfig=tryreadconfig('config.json')
postprocessconfig=tryreadconfig('postprocessconfig.json')
noundictconfig=tryreadconfig('noundictconfig.json')
transerrorfixdictconfig=tryreadconfig('transerrorfixdictconfig.json')
savehook_new=tryreadconfig('savehook_new.json') 


def syncconfig(config,default):
    for key in default:
        if key not in config:
            config[key]=default[key]
        if type(default[key])==dict:
            syncconfig(config[key],default[key])
    for key in list(config.keys()):
        if key not in default:
            config.pop(key)
        
syncconfig(transerrorfixdictconfig,defaulterrorfix)
syncconfig(postprocessconfig,defaultpost)
syncconfig(noundictconfig,defaultnoun)
syncconfig(globalconfig,defaultglobalconfig)
 
#0 ja  1 eng