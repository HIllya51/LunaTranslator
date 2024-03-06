
from translator.basetranslator import basetrans
import json,requests
from myutils.config import globalconfig
import websocket,time,os
from traceback import print_exc
class basetransdev(basetrans): 
    target_url=None
    def check_url_is_translator_url(self,url):
        return url.startswith(self.target_url)
    
    def Page_navigate(self,url):
        self._SendRequest('Page.navigate',{'url':url})
        self._wait_document_ready()
    def Runtime_evaluate(self,expression):
        return self._SendRequest('Runtime.evaluate',{"expression":expression})  
    def wait_for_result(self,expression,badresult=''):
        for i in range(10000):
            if self.using==False:return
            state =self.Runtime_evaluate(expression)
            try:
                if state['result']['value']!=badresult:
                    return state['result']['value']
            except:
                pass
            time.sleep(0.1)
#########################################
    def _private_init(self):
        self._id=1
        self._createtarget()  
        super()._private_init()
    def _SendRequest(self,method,params,ws=None):
        if self.using==False:return
        self._id+=1
        try:
            if ws is None:ws=self.ws
            ws.send(json.dumps({'id':self._id,'method':method,'params':params}))
            res=ws.recv()
        except :
            print_exc()
            self._createtarget()
            time.sleep(1)
            return self._SendRequest(method,params,ws)
        res=json.loads(res)
        try:    
            return res['result']
        except:
            print(res)
            if res['method']=='Inspector.detached' and res['params']['reason']=='target_closed':
                self._createtarget()
                return self._SendRequest(method,params,ws)
     

    def _createtarget(self): 
        if self.using==False:return
        port=globalconfig['debugport']
        url=self.target_url
        try:
            infos=requests.get('http://127.0.0.1:{}/json/list'.format(port)).json() 
        except :
            print_exc()
            time.sleep(1)
            self._createtarget()
            return
        use=None
        for info in infos: 
            if self.check_url_is_translator_url(info['url']):
                use=info['webSocketDebuggerUrl']
                break
        if use is None: 
                ws=websocket.create_connection(infos[0]['webSocketDebuggerUrl'])  
                a=self._SendRequest('Target.createTarget',{'url':url},ws=ws)  
                 
                use= 'ws://127.0.0.1:{}/devtools/page/'.format(port)+a['targetId']
        self.ws=websocket.create_connection(use)  
        self._wait_document_ready()
    
    def _wait_document_ready(self):  
        for i in range(10000):
            if self.using==False:return
            state =self.Runtime_evaluate( "document.readyState")
            try:
                if state['result']['value']=='complete':
                    break
            except:
                pass
            time.sleep(0.1)
    def send_keys(self,text):
        self._SendRequest('Input.setIgnoreInputEvents', {'ignore': False})
        try:
            self._SendRequest('Input.insertText', {'text': text})
        except:
            for char in text:
                #self._SendRequest('Input.dispatchKeyEvent', {'type': 'keyDown', 'modifiers': 0, 'timestamp': 0, 'text': char, 'unmodifiedText': char, 'keyIdentifier': '', 'code': f'Key{char.upper()}', 'key': char, 'windowsVirtualKeyCode': code, 'nativeVirtualKeyCode': code, 'autoRepeat': False, 'isKeypad': False, 'isSystemKey': False, 'location': 0})
                self._SendRequest('Input.dispatchKeyEvent', {'type': 'char', 'modifiers': 0, 'timestamp': 0, 'text': char, 'unmodifiedText': char, 'keyIdentifier': '', 'code': 'Unidentified', 'key': '', 'windowsVirtualKeyCode': 0, 'nativeVirtualKeyCode': 0, 'autoRepeat': False, 'isKeypad': False, 'isSystemKey': False, 'location': 0})
                #self._SendRequest('Input.dispatchKeyEvent', {'type': 'keyUp', 'modifiers': 0, 'timestamp': 0, 'text': '', 'unmodifiedText': '', 'keyIdentifier': '', 'code': f'Key{char.upper()}', 'key': char, 'windowsVirtualKeyCode': code, 'nativeVirtualKeyCode': code, 'autoRepeat': False, 'isKeypad': False, 'isSystemKey': False, 'location': 0})
            
        self._SendRequest('Input.setIgnoreInputEvents', {'ignore': True})
    