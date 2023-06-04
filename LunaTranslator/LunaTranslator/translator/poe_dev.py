 
from traceback import print_exc
import requests,os
from urllib.parse import quote
import re

from urllib.parse import quote
import websocket as websockets
import json
from utils.subproc import subproc_w
from utils.config import globalconfig
import json  
from translator.basetranslator import basetrans
import time,hashlib

_id=1
def SendRequest(websocket,method,params):
    global _id
    _id+=1
    websocket.send(json.dumps({'id':_id,'method':method,'params':params}))
    res=websocket.recv()
    return json.loads(res)['result']
  

def waitload( websocket):  
        for i in range(10000):
            state =(SendRequest(websocket,'Runtime.evaluate',{"expression":"document.readyState"})) 
            if state['result']['value']=='complete':
                break
            time.sleep(0.1)

def waittransok( websocket,index):   
        # print(f'(father.length>={index}+1)?((father[{index}].children.length>=2)?(father[{index}].children[1].dataset.complete):""):""')
        # print(f'(father.length>={index}+1)?((father[{index}].children.length>=2)?(father[{index}].children[1].dataset.complete?father[{index}].children[1].innerText:""):""):""')
        for i in range(10000):
            state =(SendRequest(websocket,'Runtime.evaluate',{"expression":f'(document.getElementsByClassName("ChatMessagesView_messagePair__CsQMW").length>={index}+1)?((document.getElementsByClassName("ChatMessagesView_messagePair__CsQMW")[{index}].children.length>=2)?(document.getElementsByClassName("ChatMessagesView_messagePair__CsQMW")[{index}].children[1].dataset.complete):""):""',"returnByValue":True}))   
            if state['result']['value'] =='true':
                 
                state =(SendRequest(websocket,'Runtime.evaluate',{"expression":f'document.getElementsByClassName("ChatMessagesView_messagePair__CsQMW")[{index}].children[1].textContent',"returnByValue":True}))  
                return state['result']['value']
            time.sleep(0.1)
        return ''
def getcurrentidx( websocket):  
        
        for i in range(10000):
            state =(SendRequest(websocket,'Runtime.evaluate',{"expression":"document.getElementsByClassName('ChatMessagesView_messagePair__CsQMW').length;","returnByValue":True}))  
            if state['result']['value']!='':
                return state['result']['value']
            time.sleep(0.1)
        return ''
def tranlate(websocketurl,content,src,tgt ): 
    if 1:
        
        websocket= websockets.create_connection(websocketurl)  
        index=getcurrentidx(websocket)
        print(index)
        SendRequest(websocket,'Runtime.evaluate',{"expression":f'''i=document.evaluate('//*[@id="__next"]/div[1]/div/section/div[2]/div/div/footer/div/div/div/textarea',document).iterateNext();
        b=document.evaluate('//*[@id="__next"]/div[1]/div/section/div[2]/div/div/footer/div/div/button[2]',document).iterateNext();
        i.value=`{content}`;
        b.click();'''}) 
        
        res=waittransok(websocket,index)
        
        return (res)


def createtarget(port  ): 
    url='https://poe.com/'
    infos=requests.get(f'http://127.0.0.1:{port}/json/list').json() 
    use=None
    for info in infos:
         if info['url'][:len(url)]==url:
              use=info['webSocketDebuggerUrl']
              break
    if use is None:
        if 1:
            websocket=websockets.create_connection(infos[0]['webSocketDebuggerUrl'])  
            a=SendRequest(websocket,'Target.createTarget',{'url':url})  
            use= 'ws://127.0.0.1:81/devtools/page/'+a['targetId']
    return use
class TS(basetrans): 
    def inittranslator(self ) :  
            self.websocketurl=(createtarget(globalconfig['debugport'] )) 
            ((tranlate(self.websocketurl,self.config['promt'],self.srclang,self.tgtlang)))
    def translate(self,content):  
        return((tranlate(self.websocketurl,content,self.srclang,self.tgtlang)))
        