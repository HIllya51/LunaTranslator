from ctypes import c_uint,c_bool,POINTER,c_int,c_uint64,c_wchar_p,pointer,CDLL
import platform,os

if platform.architecture()[0]=='64bit':
    bit='64' 
else:
    bit='32' 
utilsdll=CDLL(os.path.abspath(f'./files/plugins/winsharedutils{bit}.dll') )
_SetProcessMute=utilsdll.SetProcessMute
_SetProcessMute.argtypes=c_uint,c_bool

_GetProcessMute=utilsdll.GetProcessMute
_GetProcessMute.restype=c_bool

_SAPI_List=utilsdll.SAPI_List
_SAPI_List.argtypes=POINTER(c_uint64),
_SAPI_List.restype=POINTER(c_wchar_p)


_SAPI_Speak=utilsdll.SAPI_Speak
_SAPI_Speak.argtypes=c_wchar_p,c_uint,c_uint,c_uint,c_wchar_p
_SAPI_Speak.restype=c_bool

def SetProcessMute(pid,mute):
    _SetProcessMute(pid,mute)
def GetProcessMute(pid):
    return _GetProcessMute(pid)

def SAPI_List(): 
    num=c_uint64()
    _list=_SAPI_List(pointer(num))
    ret=[]
    for i in range(num.value):
        ret.append(_list[i])
    return ret  #这里没有free分配的wchar_t*，会内存泄露。不过影响不大。

def SAPI_Speak(content,voiceid,  rate,  volume,  Filename):
     
    return _SAPI_Speak(content,voiceid,  int(rate),  int(volume),  Filename)