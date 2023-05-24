 
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
import time
import time,hashlib
def b64string(a): 
    return hashlib.md5(a.encode('utf8')).digest().hex()

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
            state =(await SendRequest(websocket,'Runtime.evaluate',{"expression":"document.querySelector('.lmt__side_container--target [data-testid=translator-target-input]').textContent","returnByValue":True})) 
            if state['result']['value']!='':
                return state['result']['value']
            time.sleep(0.1)
        return ''
async def tranlate(websocketurl,content,src,tgt ): 
    async with websockets.connect(websocketurl) as websocket: 
        await SendRequest(websocket,'Page.navigate',{'url':f'https://www.deepl.com/en/translator#{src}/{tgt}/{quote(content)}'})
        await waitload(websocket)
        res=await waittransok(websocket)
        return (res)
         
class TS(basetrans):
    # def end(self):
    #     try:
    #         self.engine.kill() 
    #     except:
    #         pass 
    def inittranslator(self ) : 
                 
        self.path=None 
        self.websocketurl=None
        self.checkpath()
    def checkpath(self):
        if self.websocketurl is None:
            port =self.config['port']
            try:
                info=requests.get(f'http://127.0.0.1:{port}/json/list').json()
                websocketurl=info[0]['webSocketDebuggerUrl']
                self.websocketurl=websocketurl
            except:
                print_exc()
                _path=self.config['chrome路径']
                if _path=="":
                    return False
                if os.path.exists(_path)==False:
                    return False
                if  _path!=self.path :
                    self.path=_path 
                    
                    call="\"%s\" --proxy-server=direct:// --disable-extensions --disable-gpu --no-first-run  --remote-debugging-port=%d  --user-data-dir=\"%s\"" %( self.path ,port,os.path.abspath('./chrome_cache/deepl_'+b64string(_path))) 
                    print(call)
                    self.engine=subproc_w(call) 
                    info=requests.get(f'http://127.0.0.1:{port}/json/list').json()
                    websocketurl=info[0]['webSocketDebuggerUrl']
                    print(websocketurl)
                    self.websocketurl=websocketurl
            return(asyncio.run(tranlate(self.websocketurl,'init','','')))
    def translate(self,content): 
        self.checkpath()  
        return(asyncio.run(tranlate(self.websocketurl,content,self.srclang,self.tgtlang)))
        