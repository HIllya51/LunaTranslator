STRING = 12

MESSAGE_SIZE = 500
PIPE_BUFFER_SIZE = 50000
SHIFT_JIS = 932
MAX_MODULE_SIZE = 120
PATTERN_SIZE = 30
HOOK_NAME_SIZE = 60
FIXED_SPLIT_VALUE = 0x10001
import ctypes
from ctypes import Structure,c_int,c_char,c_uint64,c_uint,sizeof,c_wchar,c_short,c_uint32,c_bool,c_ubyte
class HostNotificationType(c_int):
    pass

HOST_NOTIFICATION_TEXT=0
HOST_NOTIFICATION_NEWHOOK=1
HOST_NOTIFICATION_FOUND_HOOK=2 
HOST_NOTIFICATION_RMVHOOK=3
HOST_NOTIFICATION_INSERTHOOK=4
class HostCommandType(c_uint):
    pass
HOST_COMMAND_NEW_HOOK=0
HOST_COMMAND_REMOVE_HOOK=1
HOST_COMMAND_FIND_HOOK=2
HOST_COMMAND_MODIFY_HOOK=3
HOST_COMMAND_HIJACK_PROCESS=4
HOST_COMMAND_DETACH=5
HOST_COMMAND_NEW_HOOK_NAIVE=6

class ThreadParam(Structure):
    _fields_=[
        ('processId',c_uint),
        ('addr',c_uint64),
        ('ctx',c_uint64),
        ('ctx2',c_uint64)
    ]   
    def __hash__(self):
        return hash((self.processId, self.addr,self.ctx,self.ctx2))
    def __eq__(self, __value ):
        return self.__hash__()==__value.__hash__()

class HookParam(Structure):
    _fields_=[
        ('address',c_uint64),
        ('offset',c_int),
        ('index',c_int),
        ('split',c_int),
        ('split_index',c_int),
        ('null_length',c_int),
        ('module',c_wchar*MAX_MODULE_SIZE),
        ('function',c_char*MAX_MODULE_SIZE),
        ('type',c_uint),
        ('codepage', c_uint),
        ('length_offset',c_short),
        ('padding',c_uint64),   #uintptr_t
        ('user_value',c_uint),
        ('text_fun',c_uint64),
        ('filter_fun',c_uint64),
        ('hook_fun',c_uint64),
        ('length_fun',c_uint64),  #函数指针
        ('_1',c_uint64),
        ('_2',c_uint64),  
        ('_3',c_uint64),  
        ('_4',c_uint64),  
        ('name',c_char*HOOK_NAME_SIZE)
    ] 
class TextHook(Structure):
    _fields_=[
        ('hp',HookParam),
        ('address',c_uint64),  #union{uint64 && void*}
        ('useCount',c_uint),
        ('readerThread',c_uint64), #HANLDE ->void*
        ('readerEvent',c_uint64),
        ('err',c_bool),
        ('trampoline',c_ubyte*140),
        ('local_buffer',c_uint64)
    ]
MAX_HOOK=2500   

class SearchParam(Structure):
    _fields_=[
        ('pattern',c_char*30),
        ('address_method',c_int),
        ('search_method',c_int),
        ('length',c_int),
        ('offset',c_int),
        ('searchTime',c_int),
        ('maxRecords',c_int),
        ('codepage',c_int), 
        ('padding',c_uint64), 
        ('minAddress',c_uint64), 
        ('maxAddress',c_uint64),
        ('boundaryModule',c_wchar*120),
        ('exportModule',c_wchar*120),
        ('text',c_wchar*30)
    ] 


class DetachCmd(Structure):
    _fields_=[
        ('command',HostCommandType),
    ]
    def __init__(self) -> None:
        self.command=HOST_COMMAND_DETACH
class RemoveHookCmd(Structure):
    _fields_=[
        ('command',HostCommandType),
        ('address',c_uint64)
    ]
    def __init__(self, address) -> None:
        self.command=HOST_COMMAND_REMOVE_HOOK
        self.address=address

class InsertHookCmd(Structure):
    _fields_=[
        ('command',HostCommandType),
        ('hp',HookParam)
    ]
    def __init__(self, hp) -> None:
        self.command=HOST_COMMAND_NEW_HOOK
        self.hp=hp
class InsertHookCodeNaive(Structure):
    _fields_=[
        ('command',HostCommandType),
        ('hcode',c_wchar*500)
    ]
    def __init__(self, hp) -> None:
        self.command=HOST_COMMAND_NEW_HOOK_NAIVE
        self.hcode=hp

class FindHookCmd(Structure):
    _fields_=[
        ('command',HostCommandType),
        ('sp',SearchParam)
    ]
    def __init__(self, sp) -> None:
        self.command=HOST_COMMAND_FIND_HOOK
        self.sp=sp
class RemoveHookCmd(Structure):
    _fields_=[
        ('command',HostCommandType),
        ('address',c_uint64)
    ]
    def __init__(self, address) -> None:
        self.command=HOST_COMMAND_REMOVE_HOOK
        self.address=address  
class hookfoundtext(Structure):
    _fields_=[('text',c_wchar*MESSAGE_SIZE)]


class HookFoundNotif(Structure):
	_fields_=[
        ('command',HostNotificationType),
        ('hp',HookParam),
        ('hcode',c_wchar*500),
        ('text',hookfoundtext)
    ] 
class ConsoleOutputNotif(Structure):
	_fields_=[
        ('command',HostNotificationType),
        ('message',c_char*MESSAGE_SIZE)
    ] 
class HookRemovedNotif(Structure):
    _fields_=[
        ('command',HostNotificationType),
        ('address',c_uint64)
    ]  
class HookInsertingNotif(Structure):
    _fields_=[
         ('command',HostNotificationType),
        ('addr',c_uint64), 
    ]  
SHAREDMEMDPREFIX='LUNA_VNR_SECTION_'
HOOKCODEGET='LUNA_HOOKCODE_'

HOOK_PIPE_NAME="\\\\.\\pipe\\LUNA_HOOK"
HOST_PIPE_NAME="\\\\.\\pipe\\LUNA_HOST"
PIPE_AVAILABLE_EVENT = "LUNA_PIPE_AVAILABLE"


class Hookcodeshared(Structure):
    _fields_=[('code',c_wchar*500)]

class EmbedSharedMem(ctypes.Structure):
	_fields_=[
		('using',ctypes.c_uint64*10),
		('addr',ctypes.c_uint64*10),
		('ctx1',ctypes.c_uint64*10),
		('ctx2',ctypes.c_uint64*10),
		('waittime',ctypes.c_uint32),
		('spaceadjustpolicy',ctypes.c_uint32),
        ('keeprawtext',ctypes.c_uint32),
		('hash',ctypes.c_uint64),
		('text',ctypes.c_wchar*1000),
          ('fontCharSetEnabled',ctypes.c_bool),
          ('fontCharSet',ctypes.c_uint8), 
          ('fontFamily',ctypes.c_wchar*100), 
    ]
        
EMBED_SHARED_MEM="EMBED_SHARED_MEM"

LUNA_NOTIFY="LUNA_NOTIFY.%s.%s"
ITH_HOOKMAN_MUTEX_="LUNA_VNR_HOOKMAN_"