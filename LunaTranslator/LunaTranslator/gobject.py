baseobject=None
from traceback import print_exc
import re
 
def gprint(*args, sep=' ', end='\n'):
    try:
        output = sep.join(str(arg) for arg in args)+end  
        baseobject.transhis.getdebuginfosignal.emit(output)
    except:
        print(args, sep=' ', end='\n')
        print_exc()