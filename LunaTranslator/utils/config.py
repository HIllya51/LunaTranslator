import json 
import os 
from collections import OrderedDict
if os.path.exists('./userconfig')==False:
    os.mkdir('./userconfig')
if os.path.exists('./transkiroku')==False:
    os.mkdir('./transkiroku')
if os.path.exists('./ttscache/')==False:
    os.mkdir('./ttscache/')
if os.path.exists('./capture')==False:
    os.mkdir('./capture')

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
def tryreadconfig2(path): 
    path=os.path.join('./files/defaultconfig/',path)
    with open(path,'r',encoding='utf-8') as ff:
        x=json.load(ff) 
    return x 
defaultpost=tryreadconfig2('postprocessconfig.json')
defaultglobalconfig=tryreadconfig2('config.json')
defaulterrorfix=tryreadconfig2('transerrorfixdictconfig.json')
defaultnoun=tryreadconfig2('noundictconfig.json')
translatordfsetting=tryreadconfig2('translatorsetting.json')
ocrdfsetting=tryreadconfig2('ocrsetting.json')

globalconfig=tryreadconfig('config.json')
postprocessconfig=tryreadconfig('postprocessconfig.json')
noundictconfig=tryreadconfig('noundictconfig.json')
transerrorfixdictconfig=tryreadconfig('transerrorfixdictconfig.json')
savehook_new=OrderedDict(tryreadconfig('savehook_new.json') )
savehook_new2=tryreadconfig('savehook_new3.json') 

translatorsetting=tryreadconfig('translatorsetting.json') 
ocrsetting=tryreadconfig('ocrsetting.json') 

def syncconfig(config,default,drop=False,deep=0):
    
    for key in default: 
        if key not in config: 
            config[key]=default[key] 
        elif key=='name': 
            config[key]=default[key]
        if type(default[key])!=type(config[key]) and (type(default[key])==dict or type(default[key])==list): 
            config[key]=default[key] 
        elif type(default[key])==dict:  
            syncconfig(config[key],default[key],drop,deep-1)
             
    if drop and deep>0:
        for key in list(config.keys()):
            if key not in default:
                config.pop(key) 
def listlengthsync(d1,d2,key,force=False):
    
    if force or  len(d1[key])!=len(d2[key]):
        d1[key]=d2[key]
syncconfig(postprocessconfig,defaultpost ,True,3) 
syncconfig(globalconfig,defaultglobalconfig)
 
syncconfig(transerrorfixdictconfig,defaulterrorfix)

syncconfig(noundictconfig,defaultnoun)
syncconfig(translatorsetting,translatordfsetting)


syncconfig(ocrsetting,ocrdfsetting,True,3)

def synccishu():
    for k in ['xiaoxueguan','edict','edict2','linggesi']:
        if k in globalconfig:
            
                globalconfig['cishu'][k]['path']=(globalconfig[k]['path'])
                globalconfig.pop(k)
synccishu()
try:
    if 'mecab' in globalconfig  :
        globalconfig['hirasetting']['mecab']['path']=globalconfig['mecab']['path']
        globalconfig['hirasetting']['mecab']['use']=globalconfig['mecab']['use']
        globalconfig.pop('mecab')
except:
    pass
listlengthsync(globalconfig,defaultglobalconfig,'postprocess_rank') 
listlengthsync(globalconfig,defaultglobalconfig,'language_list',True) 
listlengthsync(globalconfig,defaultglobalconfig,'language_list_translator',True) 
listlengthsync(globalconfig,defaultglobalconfig,'normallanguagelist',True) 
for fanyi in globalconfig['fanyi']:
    try:
        listlengthsync(globalconfig['fanyi'][fanyi],defaultglobalconfig['fanyi'][fanyi],'lang',True) 
    except:
        pass
for fanyi in globalconfig['ocr']:
    try:
        listlengthsync(globalconfig['ocr'][fanyi],defaultglobalconfig['ocr'][fanyi],'lang',True) 
    except:
        pass

def setlanguage():
    global language,languageshow
    language=globalconfig['languageuse']
    with open(f'./files/lang/{globalconfig["language_list"][language]}.json','r',encoding='utf8') as ff:
        languageshow=json.load(ff)
setlanguage()
def _TR(k):
    global language,languageshow
     
    if k=='':
        return ''
    if k not in languageshow or languageshow[k]=='':
        languageshow[k]='' 
        with open(f'./files/lang/{globalconfig["language_list"][language]}.json','w',encoding='utf8') as ff:
            ff.write( json.dumps(languageshow,ensure_ascii=False,sort_keys=False, indent=4))
        return k
    else:
        return languageshow[k]
def _TRL(kk):
    x=[]
    for k in kk:
        x.append(_TR(k))
    return x



def saveallconfig():
        
        with open('./userconfig/config.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps(globalconfig,ensure_ascii=False,sort_keys=False, indent=4))
         
        with open('./userconfig/postprocessconfig.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps(postprocessconfig,ensure_ascii=False,sort_keys=False, indent=4))
        with open('./userconfig/transerrorfixdictconfig.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps(transerrorfixdictconfig,ensure_ascii=False,sort_keys=False, indent=4))
        with open('./userconfig/noundictconfig.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps(noundictconfig,ensure_ascii=False,sort_keys=False, indent=4))
        with open('./userconfig/translatorsetting.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps(translatorsetting,ensure_ascii=False,sort_keys=False, indent=4))
        with open('./userconfig/ocrsetting.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps(ocrsetting,ensure_ascii=False,sort_keys=False, indent=4))

        with open('./userconfig/savehook_new.json','w',encoding='utf8') as ff:
                ff.write(json.dumps(savehook_new,ensure_ascii=False,sort_keys=False, indent=4))
        with open('./userconfig/savehook_new3.json','w',encoding='utf8') as ff:
                ff.write(json.dumps(savehook_new2,ensure_ascii=False,sort_keys=False, indent=4))