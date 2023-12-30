baseobject=None
from traceback import print_exc
import io,sys

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

