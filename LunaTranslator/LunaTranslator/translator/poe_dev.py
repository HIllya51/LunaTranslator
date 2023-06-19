 
from traceback import print_exc
import requests,os
from urllib.parse import quote
import re

from urllib.parse import quote
import websocket as websockets
import json
from myutils.subproc import subproc_w
from myutils.config import globalconfig
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
         
        for i in range(10000):
            state =(SendRequest(websocket,'Runtime.evaluate',{"expression":'(document.getElementsByClassName("ChatMessagesView_messagePair__CsQMW").length>={}+1)?((document.getElementsByClassName("ChatMessagesView_messagePair__CsQMW")[{}].children.length>=2)?(document.getElementsByClassName("ChatMessagesView_messagePair__CsQMW")[{}].children[1].dataset.complete):""):""'.format(index,index,index),"returnByValue":True}))   
            if state['result']['value'] =='true':
                 
                state =(SendRequest(websocket,'Runtime.evaluate',{"expression":'document.getElementsByClassName("ChatMessagesView_messagePair__CsQMW")[{}].children[1].textContent'.format(index),"returnByValue":True}))  
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
        SendRequest(websocket,'Runtime.evaluate',{"expression":'''i=document.evaluate('//*[@id="__next"]/div[1]/div/section/div[2]/div/div/footer/div/div/div/textarea',document).iterateNext();
        b=document.evaluate('//*[@id="__next"]/div[1]/div/section/div[2]/div/div/footer/div/div/button[2]',document).iterateNext();
        i.value=`{}`;
        b.click();'''.format(content)}) 
        
        res=waittransok(websocket,index)
        
        return (res)


def createtarget(port  ): 
    url='https://poe.com/'
    infos=requests.get('http://127.0.0.1:{}/json/list'.format(port)).json() 
    use=None
    for info in infos:
         if info['url'][:len(url)]==url:
              use=info['webSocketDebuggerUrl']
              break
    if use is None:
        if 1:
            websocket=websockets.create_connection(infos[0]['webSocketDebuggerUrl'])  
            a=SendRequest(websocket,'Target.createTarget',{'url':url})  
            use= 'ws://127.0.0.1:{}/devtools/page/'.format(port)+a['targetId']
    return use
class TS(basetrans): 
    def inittranslator(self ) :  
            self.websocketurl=(createtarget(globalconfig['debugport'] )) 
            ((tranlate(self.websocketurl,self.config['promt'],self.srclang,self.tgtlang)))
    def translate(self,content):  
        return((tranlate(self.websocketurl,content,self.srclang,self.tgtlang)))
        