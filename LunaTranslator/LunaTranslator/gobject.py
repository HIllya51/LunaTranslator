baseobject=None
from traceback import print_exc
import io,sys,platform,os
isbit64= platform.architecture()[0]=='64bit'
DLL3264path=os.path.abspath('files/plugins/DLL'+('32','64')[isbit64])
def GetDllpath(_):
    if isinstance(_,str):
        return os.path.join(DLL3264path,_)
    elif isinstance(_,(list,tuple)):
        return os.path.join(DLL3264path,_[isbit64])
class debugoutput(io.IOBase):
    def __init__(self,idx,file=sys.stdout) -> None:
        super().__init__()
        self.idx=idx
        self.originfile=file
    def write(self,data):
        if self.originfile:
            self.originfile.write(data)
        baseobject.transhis.getdebuginfosignal.emit(self.idx,str(data))
    def flush(self):
        if self.originfile:
            self.originfile.flush()


_jsconsole=debugoutput('jsconsole',sys.stdout)
def overridestdio():
    sys.stderr=debugoutput('stderr',sys.stderr)
    sys.stdout=debugoutput('stdout',sys.stdout)
def gprint(*args,**kwargs):  
    kwargs['file']=_jsconsole
    print(*args,**kwargs)

