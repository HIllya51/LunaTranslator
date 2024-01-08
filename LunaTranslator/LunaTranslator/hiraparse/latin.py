from myutils.config import globalconfig

from myutils.utils import getproxy
import os,requests
from traceback import print_exc
class hira:
    def __init__(self) -> None: 
        pass 
     
    def fy(self,text): 
        _x=[]
        i=0
        for _ in text.split(' '):
            if i:
                _x.append({'orig':' ','hira':''})
            
            _x.append({'orig':_,'hira':''})
            i+=1
        return _x