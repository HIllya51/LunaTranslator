 
from traceback import print_exc
import requests,os
from urllib.parse import quote
import re

from urllib.parse import quote
import websockets
import asyncio,json
from utils.subproc import subproc_w
from utils.config import globalconfig
import json  
from translator.basetranslator import basetrans
import time,hashlib

_id=1
async def SendRequest(websocket,method,params):
    global _id
    _id+=1
    await websocket.send(json.dumps({'id':_id,'method':method,'params':params}))
    res=await websocket.recv()
    return json.loads(res)['result']
  

async def waitload( websocket):  
        for i in range(10000):
            state =(await SendRequest(websocket,'Runtime.evaluate',{"expression":"document.readyState"})) 
            if state['result']['value']=='complete':
                break
            time.sleep(0.1)

async def waittransok( websocket):  
        for i in range(10000):
            state =(await SendRequest(websocket,'Runtime.evaluate',{"expression":'document.querySelector("#target-textblock").innerText',"returnByValue":True}))  
            if state['result']['value']!='':
                return state['result']['value']
            time.sleep(0.1)
        return ''
async def tranlate(websocketurl,content,src,tgt ): 
    async with websockets.connect(websocketurl) as websocket: 
        await SendRequest(websocket,'Runtime.evaluate',{"expression":f'i=document.querySelector("#textarea");i.value=``;event = new Event("input", {{bubbles: true, cancelable: true }});i.dispatchEvent(event);i.value=`{content}`;event = new Event("input", {{bubbles: true, cancelable: true }});i.dispatchEvent(event);'}) 
       
        await waitload(websocket)
        res=await waittransok(websocket)
        return (res)


async def createtarget(port  ): 
    url='https://fanyi.caiyunapp.com/#/'
    infos=requests.get(f'http://127.0.0.1:{port}/json/list').json() 
    use=None
    for info in infos:
         if info['url'][:len(url)]==url:
              use=info['webSocketDebuggerUrl']
              break
    if use is None:
        
        async with websockets.connect(infos[0]['webSocketDebuggerUrl']) as websocket: 
            a=await SendRequest(websocket,'Target.createTarget',{'url':url})  
            use= 'ws://127.0.0.1:81/devtools/page/'+a['targetId']
    return use
class TS(basetrans): 
    def inittranslator(self ) :  
            self.websocketurl=asyncio.run(createtarget(globalconfig['debugport'] )) 
    def translate(self,content):  
        return(asyncio.run(tranlate(self.websocketurl,content,self.srclang,self.tgtlang)))
        