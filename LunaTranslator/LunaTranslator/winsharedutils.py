from ctypes import c_uint,c_bool,POINTER,c_char_p,c_uint64,c_wchar_p,pointer,CDLL,c_int,Structure,c_void_p,cast,memmove,create_unicode_buffer,create_string_buffer,c_size_t,windll
import os,gobject
 
utilsdll=CDLL(gobject.GetDllpath(('winsharedutils32.dll','winsharedutils64.dll')))

_freewstringlist=utilsdll.freewstringlist
_freewstringlist.argtypes=POINTER(c_wchar_p),c_uint
_free_all=utilsdll.free_all
_free_all.argtypes=c_void_p,
_freestringlist=utilsdll.freestringlist
_freestringlist.argtypes=POINTER(c_char_p),c_uint

_SetProcessMute=utilsdll.SetProcessMute
_SetProcessMute.argtypes=c_uint,c_bool

_GetProcessMute=utilsdll.GetProcessMute
_GetProcessMute.restype=c_bool

_SAPI_List=utilsdll.SAPI_List
_SAPI_List.argtypes=c_uint,POINTER(c_uint64),
_SAPI_List.restype=POINTER(c_wchar_p)


_SAPI_Speak=utilsdll.SAPI_Speak
_SAPI_Speak.argtypes=c_wchar_p,c_uint,c_uint,c_uint,c_uint,c_wchar_p
_SAPI_Speak.restype=c_bool



_levenshtein_distance=utilsdll.levenshtein_distance
_levenshtein_distance.argtypes=c_uint,c_wchar_p,c_uint,c_wchar_p
_levenshtein_distance.restype=c_uint #实际上应该都是size_t，但size_t 32位64位宽度不同，都用32位就行了，用int64会内存越界

_mecab_init=utilsdll.mecab_init
_mecab_init.argtypes=c_char_p,c_wchar_p
_mecab_init.restype=c_void_p

_mecab_parse=utilsdll.mecab_parse
_mecab_parse.argtypes=c_void_p,c_char_p,POINTER(POINTER(c_char_p)),POINTER(POINTER(c_char_p)),POINTER(c_uint)
_mecab_parse.restype=c_bool

_mecab_end=utilsdll.mecab_end
_mecab_end.argtypes=c_void_p,

_clipboard_get=utilsdll.clipboard_get
_clipboard_get.restype=c_void_p  #实际上是c_wchar_p，但是写c_wchar_p 傻逼python自动转成str，没法拿到指针
_clipboard_set=utilsdll.clipboard_set
_clipboard_set.argtypes=c_void_p,c_wchar_p,

def SetProcessMute(pid,mute):
    _SetProcessMute(pid,mute)
def GetProcessMute(pid):
    return _GetProcessMute(pid)

def SAPI_List(v): 
    num=c_uint64()
    _list=_SAPI_List(v,pointer(num))
    ret=[]
    for i in range(num.value):
        ret.append(_list[i])
    _freewstringlist(_list,num.value)
    return ret 

def SAPI_Speak(content,v,voiceid,  rate,  volume,  Filename):
     
    return _SAPI_Speak(content,v,voiceid,  int(rate),  int(volume),  Filename)




def distance(s1,s2):
    return _levenshtein_distance(len(s1),s1,len(s2),s2)
 
class mecabwrap:
    def __init__(self,mecabpath) -> None:
        self.kks=_mecab_init(mecabpath.encode('utf8'),gobject.GetDllpath('libmecab.dll') )
    def __del__(self):
        _mecab_end(self.kks)
    def parse(self,text,codec):
        surface=POINTER(c_char_p)()
        feature=POINTER(c_char_p)()
        num=c_uint()
        _mecab_parse(self.kks,text.encode(codec),pointer(surface),pointer(feature),pointer(num))
        res=[]
        for i in range(num.value):
            f=feature[i]
            fields=f.decode(codec).split(',')
            res.append((surface[i].decode(codec),fields))
        _freestringlist(feature,num.value)
        _freestringlist(surface,num.value)
        return res 
 

clphwnd=windll.user32.CreateWindowExW(0,"STATIC",0,0,0,0,0,0,0,0,0,0);
def clipboard_set(text):
    global clphwnd
    #_set_clip_board_queue.put(text)
    return _clipboard_set(clphwnd,text) 

def clipboard_get():
    p=_clipboard_get() 
    if p:
        v=cast(p,c_wchar_p).value
        _free_all(p)
        return v
    else:
        return ''
    


html_new=utilsdll.html_new
html_new.argtypes=c_void_p,
html_new.restype=c_void_p
html_navigate=utilsdll.html_navigate
html_navigate.argtypes=c_void_p,c_wchar_p
html_resize=utilsdll.html_resize
html_resize.argtypes=c_void_p,c_uint,c_uint,c_uint,c_uint
html_release=utilsdll.html_release
html_release.argtypes=c_void_p,

class HTMLBrowser():
    def __init__(self,parent) -> None:
        self.html=html_new(parent)
    def resize(self,x,y,w,h,):
        html_resize(self.html,x,y,w,h)
    def navigate(self,url):
        html_navigate(self.html,url)
    def __del__(self):
        html_release(self.html)


_GetLnkTargetPath=utilsdll.GetLnkTargetPath
_GetLnkTargetPath.argtypes=c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p
def GetLnkTargetPath(lnk):
    MAX_PATH=260
    exe=create_unicode_buffer(MAX_PATH)
    arg=create_unicode_buffer(MAX_PATH)
    icon=create_unicode_buffer(MAX_PATH)
    dirp=create_unicode_buffer(MAX_PATH)
    _GetLnkTargetPath(lnk,exe,arg,icon,dirp)
    return exe.value,arg.value,icon.value,dirp.value


_otsu_binary=utilsdll.otsu_binary
_otsu_binary.argtypes=c_void_p,c_int
def otsu_binary(image,thresh):
    buf=create_string_buffer(len(image))
    memmove(buf,image,len(image))
    _otsu_binary(buf,thresh)
    return buf

_extracticon2data=utilsdll.extracticon2data
_extracticon2data.argtypes=c_wchar_p,POINTER(c_size_t)
_extracticon2data.restype=c_void_p
def extracticon2data(fname):
    length=c_size_t()
    datap=_extracticon2data(fname,pointer(length))
    if datap :
        save=create_string_buffer(length.value) 
        memmove(save,datap,length.value) 
        _free_all(datap) 
        return save 
    else:
        return None
    
WriteMemoryCallback=utilsdll.WriteMemoryCallback
c_free=utilsdll.c_free
c_free.argtypes=c_void_p,
class MemoryStruct(Structure):
    _fields_=[
        ('memory',c_void_p),
        ('size',c_size_t)
    ]
    def __init__(self )  :
        super().__init__( )
        self.memory=0
        self.size=0
    def __del__(self):
        if self.memory:
            c_free(self.memory)