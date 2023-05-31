 
from traceback import print_exc
import requests,os
from urllib.parse import quote
import re
import winsharedutils
from urllib.parse import quote
import websockets
import asyncio,json
from utils.config import globalconfig
import json  
from translator.basetranslator import basetrans
import time
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
            state =(await SendRequest(websocket,'Runtime.evaluate',{"expression":"document.getElementsByClassName('textpanel-target-textblock')[0].innerText","returnByValue":True}))
            print(state)
            if state['result']['value']!='':
                return state['result']['value']
            time.sleep(0.1)
        return ''
async def tranlate(websocketurl,content,src,tgt ): 
    async with websockets.connect(websocketurl) as websocket:  
        tgtlist=['zh','en','ja','ko','fr','es','it','de','tr','ru','pt','vi','id','th','ms','ar','hi']
        if tgt in tgtlist:
            tgtidx=tgtlist.index(src)+1
        else:
            tgtidx=1
        
        await SendRequest(websocket,'Runtime.evaluate',{"expression":
            f'''document.querySelector('div.textpanel-tool.tool-close').click();
            document.querySelector("#language-button-group-source > div.language-button-dropdown.language-source > ul > li:nth-child(1) > span").click();
            document.querySelector("#language-button-group-target > div.language-button-dropdown.language-target > ul > li:nth-child({tgtidx}) > span");
            document.getElementsByClassName('textinput')[0].value=`{content}`;
            document.getElementsByClassName('language-translate-button')[0].click();
            '''})  
        res=await waittransok(websocket)

        #document.getElementById('tta_input_ta')
        return (res)
 

async def createtarget(port  ): 
    url='https://fanyi.qq.com/'
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
        