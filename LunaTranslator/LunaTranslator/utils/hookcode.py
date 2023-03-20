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


class HookParam:
    def __init__(self):
        self.type = 0
        self.index=0
        self.split=0
        self.split_index=0
        self.null_length=0
        self.model=''
        self.function=''
        self.address=0
        self.codepage=0
        self.length_offset=0
        self.padding=0
        self.user_value=0
        self.name='' 
import re

def ParseRcode(rcode):
    hp = HookParam()
    hp.type |= DIRECT_READ
    if rcode[0] == 'S':
        pass
    elif rcode[0] == 'Q':
        hp.type |= USING_UNICODE
    elif rcode[0] == 'V':
        hp.type |= USING_UTF8
    elif rcode[0] == 'M':
        hp.type |= USING_UNICODE
        hp.type |= HEX_DUMP
    else:
        return None
    rcode=rcode[1:]
    match=re.findall("^([0-9]+)<",rcode)
    if len(match)>0:
        hp.null_length=int(match[0])
        rcode=rcode[len(match[0])+1:]
    match=re.findall("^([0-9]+)#",rcode)
    if len(match)>0:
        hp.codepage=int(match[0])
        rcode=rcode[len(match[0])+1:]
    
    match=re.match("@([0-9a-fA-F]+)",rcode)
    if match is None:
        return None
    hp.address=int(rcode[1:],16)
    return hp
def ParseHcode(hcode):
    hp = HookParam()

    if hcode[0] == 'A':
        hp.type |= BIG_ENDIAN
        hp.length_offset=1
    elif hcode[0] == 'B':
        hp.length_offset=1
    elif hcode[0] == 'W':
        hp.type |= USING_UNICODE
        hp.length_offset=1
    elif hcode[0] == 'H':
        hp.type |= USING_UNICODE
        hp.type |= HEX_DUMP
        hp.length_offset=1
    elif hcode[0] == 'S':
        hp.type |= USING_STRING  
    elif hcode[0] == 'Q':
        hp.type |= USING_STRING  
        hp.type |= USING_UNICODE  
    elif hcode[0] == 'V':
        hp.type |= USING_STRING  
        hp.type |= USING_UTF8  
    elif hcode[0] == 'M':
        hp.type |= USING_STRING  
        hp.type |= USING_UNICODE  
        hp.type |= HEX_DUMP 
    else:
        return None
    
    hcode=hcode[1:]
    
    if hp.type & USING_STRING:
        if hcode[0]=='F':
                hp.type|=FULL_STRING
                hcode=hcode[1:]
        match=re.findall("^([0-9]+)<",hcode)
        if len(match)>0 :
                hp.null_length=int(match[0])
                hcode=hcode[len(match[0])+1:]
    
    if hcode[0]=='N':
            hp.type|=NO_CONTEXT
            hcode=hcode[1:]
    
    match=re.findall("^([0-9]+)#",hcode)
    if len(match):
            hp.codepage=int(match[0])
            hcode=hcode[len(match[0])+1:]
     
    match=re.search("^([0-9a-fA-F]+)\\+",hcode)
    if match: 
        hp.address=int(match[0][:-1],16)
        hcode=hcode[len(match[0])+1:]
    
    def ConsumeHexInt(hcode):
            size=0
            value=0
            length=0
            if hcode[0]=='-':hcode=hcode[1:]
            while True:
                    
                    try:
                        value=int(hcode[:length+1],16)
                    except ValueError: 
                        break
                    length+=1
             
            return hcode[length:],value
    hcode,hp.offset=ConsumeHexInt(hcode)
    
    if hcode[0]=='*':
            hp.type|=DATA_INDIRECT
            hcode=hcode[1:]
            hcode,hp.index=ConsumeHexInt(hcode)
    if hcode[0]==':':
            hp.type|=USING_SPLIT
            hcode=hcode[1:]
            hcode,hp.split=ConsumeHexInt(hcode)
            if hcode[0]=='*':
                    hp.type|=SPLIT_INDIRECT
                    hcode=hcode[1:]
                    hcode,hp.split_index=ConsumeHexInt(hcode)
    
    match=re.match("^@([0-9a-fA-F]+)(:.+?)?(:.+)?",hcode)
     
    if match is None:
            return None
    
    hp.address=int(match.groups()[0],16)
    if match.groups()[1]:
            hp.type|=MODULE_OFFSET 
    if match.groups()[2]:
            hp.type|=FUNCTION_OFFSET
            hp.function=match.group[3][1:]
    if hp.offset<0:
            hp.offset-=4
    if hp.split<0:
            hp.split-=4
    return hp
def Parsecode(hookcode):
    try:
        if hookcode[0] == '/':
            hookcode = hookcode[1:]
        if hookcode[0] == 'R':
            return ParseRcode(hookcode[1:])
        elif hookcode[0] == 'H':
            return ParseHcode(hookcode[1:])
        else:
            return None
    except:
         return None


# print(Parsecode('/HS-4@53C60:MemoryBlue.exe'))
# print(Parsecode('HB4@0'))
# print(Parsecode('/RS65001#@44'))
# print(Parsecode('/HQN936#-c*C:C*1C@4AA:gdi.dll:GetTextOutA'))
  
# print(Parsecode("/HQN936#-c*C:C*1C@4AA:gdi.dll:GetTextOutA"))
# print(Parsecode("HB4@0")),
# print(Parsecode("/RS65001#@44")),
# print(Parsecode("HQ@4"))
# print(Parsecode("/RW@44")),
# print(Parsecode("/HWG@33"))
#print(Parsecode('/HWN-20@11BB42:如月真綾の誘惑.exe'))
#print(Parsecode('/HQ14+-1C:8C@2287F0:GameAssembly.dll'))
 
#print(Parsecode('/HQX-8@A3A0C0:nw.dll'))