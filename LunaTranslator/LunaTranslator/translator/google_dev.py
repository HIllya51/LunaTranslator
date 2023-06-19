 
from traceback import print_exc
import requests,os
from urllib.parse import quote
import re

from urllib.parse import quote
import websocket  as websockets
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

def waittransok( websocket):  
        for i in range(10000):
            state =(SendRequest(websocket,'Runtime.evaluate',{"expression":'(a=document.querySelector("#yDmH0d > c-wiz > div > div.WFnNle > c-wiz > div.OlSOob > c-wiz > div.ccvoYb.EjH7wc > div.AxqVh > div.OPPzxe > c-wiz.sciAJc > div > div.usGWQd > div > div.lRu31 > span.HwtZe"))?a.innerText:""',"returnByValue":True}))  
            if state['result']['value']!='':
                return state['result']['value']
            time.sleep(0.1)
        return ''
def tranlate(websocketurl,content,src,tgt ): 
    if 1:
        websocket=websockets.create_connection(websocketurl)   
        SendRequest(websocket,'Runtime.evaluate',{"expression":'textarea=document.querySelector("textarea");textarea.value="";event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);textarea=document.querySelector("textarea");textarea.value=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);'.format(content)}) 
        
        waitload(websocket)
        res=waittransok(websocket)
        return (res)
def navilang(websocketurl,src,tgt ): 
    if 1:
        websocket=websockets.create_connection(websocketurl)   
        SendRequest(websocket,'Page.navigate',{'url':'https://translate.google.com/?sl={}&tl={}'.format(src,tgt)})
        waitload(websocket) 
 
def createtarget(port  ): 
    url='https://translate.google.com/'
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
    def langmap(self):
        return { "zh":"zh-CN","cht":"zh-TW"} 
    def inittranslator(self ) :  
            self.websocketurl=(createtarget(globalconfig['debugport'] )) 
    def translate(self,content):  
        if 'lastlang' not in dir(self) or self.lastlang!=(self.srclang,self.tgtlang):
            (navilang(self.websocketurl,self.srclang,self.tgtlang))
            self.lastlang=(self.srclang,self.tgtlang)
        return((tranlate(self.websocketurl,content,self.srclang,self.tgtlang)))
        