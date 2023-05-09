from ctypes import c_uint,c_bool,POINTER,c_int,c_uint64,c_wchar_p,pointer
import ctypes
utilsdll=ctypes.CDLL('./x64/Release/winsharedutils.dll')
_SetProcessMute=utilsdll.SetProcessMute
_SetProcessMute.argtypes=c_uint,c_bool

_GetProcessMute=utilsdll.GetProcessMute

pid=16548

#print(_GetProcessMute(pid))
_SetProcessMute(pid,1-_GetProcessMute(pid))



_SAPI_List=utilsdll.SAPI_List
_SAPI_List.argtypes=POINTER(c_uint64),
_SAPI_List.restype=POINTER(c_wchar_p)


_SAPI_Speak=utilsdll.SAPI_Speak
_SAPI_Speak.argtypes=c_wchar_p,c_uint,c_uint,c_uint,c_wchar_p
_SAPI_Speak.restype=c_bool

num=c_uint64()
_list=_SAPI_List(pointer(num)) 
print(num.value) 
for i in range(num.value):
    print(_list[i])

_SAPI_Speak('1ssss',1,1,100,'1.wav')