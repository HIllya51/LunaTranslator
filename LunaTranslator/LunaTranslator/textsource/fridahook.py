 
import queue
from textsource.textsourcebase import basetext
from myutils.config import globalconfig,savehook_new_data
from gobject import gprint
import gobject
import os,sys,platform
from myutils.utils import stringfyerror 
from traceback import print_exc
from myutils.dotmap import DotMap
 
def buildfridaclass(copycallback,pexe):
    try:
        import frida
    except ModuleNotFoundError:
        if platform.architecture()[0]=='64bit':
            pythonbit='64' 
        else:
            pythonbit='86' 
        sys.path.append(os.path.join(globalconfig['fridahook']['path'],'runtime/x'+pythonbit))
        import frida
    class Frida:
        def __init__(self) -> None: 
            self.session=None
        def eval_func_statPath(self,args): 
            e,t=args
            e = os.path.join(t, e)
            i = {
                'path': e ,
                'isFile': False,
                'isDir': False
                } 
            try:
                i['isFile']=os.path.isfile(e)
                i['isDir']=os.path.isdir(e)
            except:
                i['errno']=True
            return i
        def eval_fs_readFileSync(self,args):
            e,t=args
            try:
                with open(e,'r',encoding=t) as ff:
                    return ff.read()
            except:
                return None
        def eval_path_dirname(self,args):
            return os.path.dirname(args[0])
        def eval_fs_writeFileSync(self,args):
            if len(args)==2:
                e,t=args
                i='w'
            else:
                raise Exception(args)
            with open(e,i) as ff:
                ff.write(t)
        def log_handler(self,e,t):
            if e=='error' and globalconfig['fridahook']['showerror']:
                gobject.baseobject.textgetmethod('<msg_error_not_refresh>'+str(e)+' '+str(t))
            elif e=='info' and globalconfig['fridahook']['showinfo']:
                gobject.baseobject.textgetmethod('<msg_info_not_refresh>'+str(e)+' '+str(t)) 
            gprint(e,t)
            pass
        def cmd_copy(self,payload):
            gprint(payload.text )
        def cmd_default(self,payload):
            self.script.post({ 'type': payload.key })
        def cmd_rpc_send(self,payload):
            i = payload.func,
            gprint(i)
        def cmd_rpc_invoke(self,payload):
            i = payload.func,
            gprint(i)
        def cmd_eval(self,payload):
            funcs={
                '__dirname':lambda _:self.scriptdir,
                '__mission':lambda _:self.scriptjsfn,
                '_statPath':self.eval_func_statPath,
                'fs_realpathSync':lambda _:os.path.abspath(_[0]),
                'fs_readFileSync':self.eval_fs_readFileSync,
                'path_dirname':lambda _:os.path.dirname(_[0]),
                'fs_writeFileSync':self.eval_fs_writeFileSync
            } 
            func=funcs.get(payload.func) 
            s=func(payload.args)   
            if type(s)==bytes:
                self.script.post({'type':payload.key},s)
            else:
                self.script.post({'type':payload.key,'result':s})
        def cmd_prompt(self,payload):
            t=payload.text
            r=payload.default
            if not r:
                r=''
            try: 
                r= savehook_new_data[pexe]['fridahook']['prompt'][t]
            except:
                pass
            def callback(texts):
                text=texts[0]
                self.script.post({'type':payload.key,'result':text})
                try:
                    savehook_new_data[pexe]['fridahook']['prompt'].update({t:text})
                except:
                    savehook_new_data[pexe]['fridahook'].update({'prompt':{t:text}})
            gobject.baseobject.Prompt.call.emit('prompt',t,[r],[callback])
            
            
        def on_message(self,raw_message: str, data):
            e=DotMap(raw_message)
            gprint(raw_message)
            
            if "error" == e.type: 
                gprint('error',e)
                if e.description:
                    gobject.baseobject.textgetmethod('<msg_error_not_refresh>'+str(e.description))
                return
            if  0 == e.payload:
                gprint('error',e)
                return 
            payloadfunctions={
                'copy':copycallback,
                'rpc_invoke':self.cmd_rpc_invoke,
                'rpc_send':self.cmd_rpc_send,
                'eval':self.cmd_eval,
                'prompt':self.cmd_prompt
            }
            default=self.cmd_default
            func=payloadfunctions.get(e.payload.cmd,default)
            func(e.payload)
        def on_destroyed(self):
            pass
        def attach(self,target,scriptjsfn):
            session=frida.attach(target)
            self.session=session
            loader=os.path.abspath(os.path.join(globalconfig['fridahook']['path'], "scripts/libLoader.js"));
            self.scriptdir=os.path.dirname(loader)
            self.scriptjsfn=os.path.abspath(os.path.join(globalconfig['fridahook']['path'],"scripts/"+scriptjsfn));
            with open(loader,'r',encoding='utf8') as ff:
                code = ff.read()
            script =session.create_script(code); 
            self.script=script
            script.set_log_handler(self.log_handler)
            script.on('message',self.on_message) 
            script.on('destroyed',self.on_destroyed)
            script.load()
            
        def run(self,exe,scriptjsfn):
            pid=frida.spawn(exe)
            self.attach(pid,scriptjsfn) 
            frida.resume(pid)
            return pid
        def detach(self):
            if self.session:
                self.script.unload()
                self.session.detach()
    return Frida
class fridahook(basetext):
    def override_cmd_copy(self,payload):
        self.getnewdata.put(payload.text)
    def __init__(self,_type,script,pname,pid=0,hwnd=0) -> None:
        self.getnewdata=queue.Queue()
        self.hwnd=hwnd
        
        savehook_new_data[pname]['fridahook'].update({
                                'js':script,
                                'loadmethod':_type
                        })
    
        self.pname=pname
        try:
            self.showgamename()
            self.frida=buildfridaclass(self.override_cmd_copy,pname)()
            if _type==1:
                pid=self.frida.run(pname,f"{script}.js")
            elif _type==0:
                self.frida.attach(pid,f"{script}.js")
            self.pids=[pid]
        except Exception as e:
            self.pids=[]
            gobject.baseobject.textgetmethod('<msg_error_refresh>'+stringfyerror(e))
            print_exc()
        super(fridahook,self).__init__(*self.checkmd5prefix(pname))
    def end(self):
        self.frida.detach()
    def gettextthread(self ): 
        self.runonce_line=self.getnewdata.get().replace('\x00','')
        return self.runonce_line
    def gettextonce(self): 
        return self.runonce_line