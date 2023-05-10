from ctypes import c_uint,c_bool,POINTER,c_int,c_uint64,c_wchar_p,pointer,c_void_p,cast
import ctypes
utilsdll=ctypes.CDLL('./x64/Release/winsharedutils64.dll')
_SetProcessMute=utilsdll.SetProcessMute
_SetProcessMute.argtypes=c_uint,c_bool

_GetProcessMute=utilsdll.GetProcessMute

pid=16548

#print(_GetProcessMute(pid))
_SetProcessMute(pid,1-_GetProcessMute(pid))



_SAPI_List=utilsdll.SAPI_List
_SAPI_List.argtypes=POINTER(c_uint64),
_SAPI_List.restype=POINTER(c_void_p)


_SAPI_Speak=utilsdll.SAPI_Speak
_SAPI_Speak.argtypes=c_wchar_p,c_uint,c_uint,c_uint,c_wchar_p
_SAPI_Speak.restype=c_bool
_clibfree=utilsdll.clibfree
_clibfree.argtypes=c_void_p,
num=c_uint64()
_list=_SAPI_List(pointer(num)) 
print(num.value) 
for i in range(num.value):
    v=cast(_list[i],c_wchar_p)
    print(v.value)
    print(type(_list),type(_list[i]))
    _clibfree( (_list[i]))
_clibfree(_list)
_SAPI_Speak('1ssss',1,1,100,'1.wav')

levenshtein_distance=utilsdll.levenshtein_distance
levenshtein_distance.argtypes=c_uint64,c_wchar_p,c_uint64,c_wchar_p
levenshtein_distance.restype=c_uint64

def distance(s1,s2):
    return levenshtein_distance(len(s1),s1,len(s2),s2)
print(distance('Levenshtein','Lenvinsten'))
print(distance('Levenshtein','Levensthein'))
print(distance('Levenshtein','Levenshten'))
print(distance('Levenshtein','Levenshtein'))
