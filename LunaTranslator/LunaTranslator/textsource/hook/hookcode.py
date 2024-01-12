import textsource.hook.define as define
import windows
from traceback import print_exc
#import define
import re,copy
USING_STRING = 0x1  # type(data) is char * or wchar_t * and has length
USING_UNICODE = 0x2  # type(data) is wchar_t or wchar_t*
BIG_ENDIAN = 0x4  # type(data) is char
DATA_INDIRECT = 0x8
USING_SPLIT = 0x10  # use ctx2 or not
SPLIT_INDIRECT = 0x20
MODULE_OFFSET = 0x40  # address is relative to module
FUNCTION_OFFSET = 0x80  # address is relative to function
USING_UTF8 = 0x100
NO_CONTEXT = 0x200
HOOK_EMPTY = 0x400
FIXING_SPLIT = 0x800
DIRECT_READ = 0x1000  # /R read code instead of classic / H hook code
FULL_STRING = 0x2000
HEX_DUMP = 0x4000
HOOK_ENGINE = 0x8000
HOOK_ADDITIONAL = 0x10000
KNOWN_UNSTABLE = 0x20000
def ConsumeHexInt(HCode):
    match = re.match(r'^([+-]?[0-9a-fA-F]+)', HCode)
    if match:
        value = int(match.group(1), 16)
        HCode = HCode[match.end():]
        return HCode,value
    else:
        return HCode,0
def Hex(st):
    return hex(st).replace('0x','').upper()
def ParseRCode(RCode) :
    hp=define.HookParam()
    hp.type |= DIRECT_READ
    if RCode[0]=='S':
        pass
    elif RCode[0] == 'Q':
        hp.type |= USING_UNICODE
    elif RCode[0]  == 'V':
        hp.type |= USING_UTF8
    elif RCode[0]  == 'M':
        hp.type |= USING_UNICODE | HEX_DUMP
    else:
        return None
    RCode = RCode[1:]
    # [null_length<]
    match = re.match(r"^([0-9]+)<", RCode)
    if match:
        hp.null_length = int(match.group(1))
        RCode = RCode[len(match.group(0)):]
    # [codepage#]
    match = re.match(r"^([0-9]+)#", RCode)
    if match:
        hp.codepage = int(match.group(1))
        RCode = RCode[len(match.group(0)):]
    # @addr
    match = re.match(r"@([0-9a-fA-F]+)", RCode)
    if not match:
        return None
    hp.address = int(match.group(1), 16)
    return hp

def ParseHCode(HCode):
    hp=define.HookParam()
    if HCode[0] == 'A':
        hp.type |= BIG_ENDIAN
        hp.length_offset = 1
    elif HCode[0] == 'B':
        hp.length_offset = 1
    elif HCode[0] == 'W':
        hp.type |= USING_UNICODE
        hp.length_offset = 1
    elif HCode[0] == 'H':
        hp.type |= USING_UNICODE | HEX_DUMP
        hp.length_offset = 1
    elif HCode[0] == 'S':
        hp.type |= USING_STRING
    elif HCode[0] == 'Q':
        hp.type |= USING_STRING | USING_UNICODE
    elif HCode[0] == 'V':
        hp.type |= USING_STRING | USING_UTF8
    elif HCode[0] == 'M':
        hp.type |= USING_STRING | USING_UNICODE | HEX_DUMP
    else:
        return None
    HCode = HCode[1:]

    if hp.type & USING_STRING:
        if HCode[0] == 'F':
            hp.type |= FULL_STRING
            HCode = HCode[1:]
        # [null_length<]
        match = re.match(r'^([0-9]+)<', HCode)
        if match:
            hp.null_length = int(match.group(1))
            HCode = HCode[match.end():]
    # [N]
    if HCode[0] == 'N':
        hp.type |= NO_CONTEXT
        HCode = HCode[1:]
    # [codepage#]
    match = re.match(r'^([0-9]+)#', HCode)
    if match:
        hp.codepage = int(match.group(1))
        HCode = HCode[match.end():]
    # [padding+]
    match = re.match(r'^([0-9a-fA-F]+)\+', HCode)
    if match:
        hp.padding = int(match.group(1), 16)
        HCode = HCode[match.end():]
    HCode,hp.offset=ConsumeHexInt(HCode)
    # [*deref_offset1]
    if HCode[0] == '*':
        hp.type |= DATA_INDIRECT
        HCode = HCode[1:]
        HCode,hp.index=ConsumeHexInt(HCode)
    # [:split_offset[*deref_offset2]]
    if HCode[0] == ':':
        hp.type |= USING_SPLIT
        HCode = HCode[1:]
        HCode,hp.split=ConsumeHexInt(HCode)
        if HCode[0] == '*':
            hp.type |= SPLIT_INDIRECT
            HCode = HCode[1:]
            HCode,hp.split_index=ConsumeHexInt(HCode)
    # @addr[:module[:func]]
    match = re.match(r'^@([0-9a-fA-F]+)(:.+?)?(:.+)?$', HCode)
    if match is None:
        return None
    hp.address = int(match.group(1), 16)
    if match.group(2):
        hp.type |= MODULE_OFFSET
        hp.module = match.group(2)[1:]
    if match.group(3):
        hp.type |= FUNCTION_OFFSET
        hp.function =bytes(match.group(3)[1:],encoding='ascii')

    # ITH has registers offset by 4 vs AGTH: need this to correct
    if hp.offset < 0:
        hp.offset -= 4
    if hp.split < 0:
        hp.split -= 4

    return hp 
def Parse(code):
    code=code.strip().replace('\r','').replace('\n','').replace('\t','')
    if(code[0]=='/'):code=code[1:]
    if('/' in code):code=code.split('/')[0]
    if(code[0]=='R'):
        hp=ParseRCode(code[1:])
    elif(code[0]=='H'):
        hp=ParseHCode(code[1:])
    else:
        hp=None
    return hp
def GenerateRCode(hp):
    RCode = 'R'
    if hp.type & USING_UNICODE:
        if hp.type & HEX_DUMP:
            RCode += 'M'
        else:
            RCode += 'Q'
        if hp.null_length != 0:
            RCode += str(hp.null_length) + '<'
    else:
        RCode += 'S'
        if hp.null_length != 0:
            RCode += str(hp.null_length) + '<'
        if hp.codepage != 0:
            RCode += str(hp.codepage) + '#'
    RCode += '@' + Hex(hp.address)
    return RCode

def GenerateHCode(hp,processId):
    HCode = "H"
    if hp.type & USING_UNICODE:
        if hp.type & HEX_DUMP:
            if hp.type & USING_STRING:
                HCode += "M"
            else:
                HCode += "H"
        else:
            if hp.type & USING_STRING:
                HCode += "Q"
            else:
                HCode += "W"
    
    else:
        if hp.type & USING_STRING:
            HCode += "S"
        elif hp.type & BIG_ENDIAN:
            HCode += "A"
        else:
            HCode += "B"
    if hp.type & FULL_STRING:
        HCode += "F"

    if hp.null_length != 0:
        HCode += str(hp.null_length) + "<"
    if hp.type & NO_CONTEXT:
        HCode += "N"
    
    if hp.text_fun or hp.filter_fun or hp.hook_fun or hp.length_fun:
        HCode += "X" # no AGTH equivalent
    if hp.codepage != 0 and not (hp.type & USING_UNICODE):
        HCode += str(hp.codepage) + "#"

    if hp.padding:
        HCode += Hex(hp.padding) + "+"
    if hp.offset < 0:
        hp.offset += 4
    
    if hp.split < 0:
        hp.split += 4
    HCode += Hex(hp.offset)
    if hp.type & DATA_INDIRECT:
        HCode += "*" + Hex(hp.index)
    if hp.type & USING_SPLIT:
        HCode += ":" + Hex(hp.split)
    if hp.type & SPLIT_INDIRECT:
        HCode += "*" + Hex(hp.split_index)
    # Attempt to make the address relative
    try:
        if processId and not (hp.type & MODULE_OFFSET):
            process =windows.AutoHandle(windows.OpenProcess(windows.PROCESS_VM_READ | windows.PROCESS_QUERY_INFORMATION, False, processId))
            if process:
                info=windows.VirtualQueryEx(process,hp.address) 
                if info.AllocationBase:
                    module_name =windows.GetModuleFileNameEx(process, info.AllocationBase)
                    if module_name:
                        hp.address -= info.AllocationBase
                        hp.type |= MODULE_OFFSET
                        hp.module = module_name[module_name.rfind('\\')+1:][:120]
              
    except:
        pass
        #print_exc()
    HCode += "@" + Hex(hp.address)

    if hp.type & MODULE_OFFSET:
        HCode += ":" + hp.module

    if hp.type & FUNCTION_OFFSET:
        HCode += ":" + hp.function.decode('ascii')
    return HCode
def Generate(_hp,process_id):
    hp=copy.copy(_hp)
    if hp.type&DIRECT_READ :
        code=GenerateRCode(hp) 
    else:
        code=GenerateHCode(hp,process_id)
     
    return code 
if __name__=='__main__':
    # print(Parse("/HQN936#1+-c*C:C*1C@4AA:gdi.dll:GetTextOutA",hp))
    # print(Parse("/HQN936#-c*C:C*1C@4AA:gdi.dll:GetTextOutA /KF",hp))
    # print(Parse("HB4@0" ,hp)),
    # print(Parse("/RS65001#@44",hp)),
    # print(Parse("HQ@4",hp,))
    print(Parse('/HS8:-14@76D85270'))
    # print(Parse("/RW@44",hp)),
    # print(Parse("/HWG@33",hp))
    