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


def syncconfig(config,default,drop=False):
    for key in default:
        if key not in config:
            config[key]=default[key]
        elif key=='name':
            config[key]=default[key]
        if type(default[key])!=type(config[key]):
            config[key]=default[key]
        elif type(default[key])==dict:
            syncconfig(config[key],default[key])
    if drop:
        for key in list(config.keys()):
            if key not in default:
                config.pop(key)
            elif type(default[key])==dict:
                syncconfig(config[key],default[key],drop)
        
syncconfig(transerrorfixdictconfig,defaulterrorfix)
syncconfig(postprocessconfig,defaultpost,True)
syncconfig(noundictconfig,defaultnoun)
syncconfig(globalconfig,defaultglobalconfig)
 
#0 ja  1 eng