import json 
import os 
from utils import somedef
from collections import OrderedDict
if os.path.exists('./userconfig')==False:
    os.mkdir('./userconfig')
if os.path.exists('./transkiroku'):
    os.rename('transkiroku','translation_record')
if os.path.exists('./translation_record')==False:
    os.mkdir('./translation_record') 
if os.path.exists('./cache')==False:
    os.mkdir('./cache')
if os.path.exists('./cache/ocr')==False:
    os.mkdir('./cache/ocr')
if os.path.exists('./cache/update')==False:
    os.mkdir('./cache/update')
if os.path.exists('./cache/screenshot')==False:
    os.mkdir('./cache/screenshot')
if os.path.exists('./cache/tts')==False:
    os.mkdir('./cache/tts')

def tryreadconfig(path,default=None):
    if os.path.exists(os.path.join('./userconfig/',path)):
        path=os.path.join('./userconfig/',path)
        with open(path,'r',encoding='utf-8') as ff:
            x=json.load(ff) 
    else:
        x=default if default else {}
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
savehook_new_0=OrderedDict(tryreadconfig('savehook_new.json') )
savehook_new_2=tryreadconfig('savehook_new3.json') 
_savehook=tryreadconfig('savehook_new_1.39.4.json',default=[[],{}])
savehook_new_list= _savehook[0]
savehook_new_data= _savehook[1]
 
def sycnsavehook():
    try: 
        for _ in savehook_new_0:
            if _ not in savehook_new_list:
                savehook_new_list.append(_) 
                savehook_new_data[_]={
                    'hook':savehook_new_0[_],
                    'leuse':savehook_new_2[_]['leuse'],
                    'title':savehook_new_2[_]['title']
                } 
        os.rename('./userconfig/savehook_new.json','./userconfig/savehook_new_backup.json')
        os.rename('./userconfig/savehook_new3.json','./userconfig/savehook_new3_backup.json')
    except:
        pass
sycnsavehook()
  
translatorsetting=tryreadconfig('translatorsetting.json') 
ocrsetting=tryreadconfig('ocrsetting.json') 

def syncconfig(config1,default,drop=False,deep=0): 
    for key in default: 
        if key not in config1: 
            config1[key]=default[key] 
             
        elif key=='name': 
            config1[key]=default[key]
        if type(default[key])!=type(config1[key]) and (type(default[key])==dict or type(default[key])==list): 
            config1[key]=default[key] 
        elif type(default[key])==dict:  
            syncconfig(config1[key],default[key],drop,deep-1)
             
    if drop and deep>0:
        for key in list(config1.keys()):
            if key not in default:
                config1.pop(key) 
def listlengthsync(d1,d2,key,force=False): 
    if force or (key not in d1) or  len(d1[key])!=len(d2[key]):
        d1[key]=d2[key]

syncconfig(globalconfig,defaultglobalconfig) 
syncconfig(postprocessconfig,defaultpost ,True,3)  
syncconfig(transerrorfixdictconfig,defaulterrorfix)

syncconfig(noundictconfig,defaultnoun)
syncconfig(translatorsetting,translatordfsetting,drop=True,deep=3)


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
 
 

def setlanguage():
    global language,languageshow
    language=globalconfig['languageuse']
    with open(f'./files/lang/{somedef.language_list[language]}.json','r',encoding='utf8') as ff:
        languageshow=json.load(ff)
setlanguage()
def _TR(k):
    global language,languageshow
     
    if k=='':
        return ''
    if k not in languageshow or languageshow[k]=='':
        languageshow[k]='' 
        
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

        
        with open('./userconfig/savehook_new_1.39.4.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps([savehook_new_list,savehook_new_data],ensure_ascii=False,sort_keys=False, indent=4))
        # with open('./userconfig/savehook_new.json','w',encoding='utf8') as ff:
        #         ff.write(json.dumps(savehook_new,ensure_ascii=False,sort_keys=False, indent=4))
        # with open('./userconfig/savehook_new3.json','w',encoding='utf8') as ff:
        #         ff.write(json.dumps(savehook_new2,ensure_ascii=False,sort_keys=False, indent=4))

        with open(f'./files/lang/{somedef.language_list[language]}.json','w',encoding='utf8') as ff:
            ff.write( json.dumps(languageshow,ensure_ascii=False,sort_keys=False, indent=4))