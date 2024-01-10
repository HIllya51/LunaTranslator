
from ctypes import CDLL,c_size_t,c_void_p,POINTER,pointer,create_string_buffer
import os,platform

dllpath=os.path.abspath(os.path.join('./files/plugins/brotli',['./x64/brotlicommon.dll','./x86/brotlicommon.dll'][platform.architecture()[0]=='32bit']))   
_brotli=CDLL(dllpath)
dllpath=os.path.abspath(os.path.join('./files/plugins/brotli',['./x64/brotlidec.dll','./x86/brotlidec.dll'][platform.architecture()[0]=='32bit']))   
_brotli=CDLL(dllpath)
BrotliDecoderDecompress=_brotli.BrotliDecoderDecompress
BrotliDecoderDecompress.argtypes=c_size_t,c_void_p,POINTER(c_size_t),c_void_p
def decompress(data): 
    size=c_size_t(1024)
    while 1:
        buff=create_string_buffer(size.value)
        succ=BrotliDecoderDecompress(len(data),data,pointer(size),buff)
        if succ==0:
            size=c_size_t(size.value*2)
        else:break 
    return buff.raw[:size.value]