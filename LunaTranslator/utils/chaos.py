from utils.config import globalconfig
 
def checkchaos(text ):
        code=globalconfig['accept_encoding']
        
        text= filter(lambda x: x not in globalconfig['accept_character'],text) 

        if globalconfig['accept_use_unicode']:
            _start=globalconfig['accept_use_unicode_start']
            _end=globalconfig['accept_use_unicode_end']
            chaos=False
            for ucode in map(lambda x:ord(x),text):
                print(ucode,_start,_end)
                if ucode<_start or ucode >_end:
                    chaos=True
                    break 
        else: 
            chaos=True 
            text=''.join(text)
            for c in code:
                try:
                    text.encode(c)
                    chaos=False
                    break
                except:
                    pass
            return chaos
import codecs
def checkencoding(code):
     
    try:
        codecs.lookup(code)
        return True
    except LookupError:
        return False