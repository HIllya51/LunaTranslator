import json 
import os ,importlib
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

translatorsetting=tryreadconfig('translatorsetting.json') 

def syncconfig(config,default,drop=False,deep=0):
    
    for key in default: 
        if key not in config: 
            config[key]=default[key] 
        elif key=='name': 
            config[key]=default[key]
        if type(default[key])!=type(config[key]) and (type(default[key])==dict or type(default[key])==list): 
            config[key]=default[key] 
        elif type(default[key])==dict:  
            syncconfig(config[key],default[key])
             
    if drop:
        for key in list(config.keys()):
            if key not in default:
                config.pop(key) 
            
            elif type(default[key])==dict and deep!=1:
                syncconfig(config[key],default[key],drop)
        
syncconfig(postprocessconfig,defaultpost ,True,1) 
syncconfig(globalconfig,defaultglobalconfig)
 
syncconfig(transerrorfixdictconfig,defaulterrorfix)

syncconfig(noundictconfig,defaultnoun)
syncconfig(translatorsetting,translatordfsetting)

for name in translatorsetting: 
    try:
        configfile=globalconfig['fanyi'][name]['argsfile']
        if os.path.exists(configfile) : 
            with open(configfile,'r',encoding='utf8') as ff:
                js=json.load(ff)  
            for k in translatorsetting[name]['args']:
                if k in js['args']:
                    translatorsetting[name]['args'][k]=js['args'][k]  
            #os.remove(configfile)
            globalconfig['fanyi'][name]['argsfile']=''
    except:
        print('error',name)
#0 ja  1 eng