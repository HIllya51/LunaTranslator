
from myutils.config import globalconfig,ocrsetting,static_data
from traceback import print_exc 
from myutils.wrapper import stripwrapper
from myutils.exceptions import ArgsEmptyExc
from myutils.utils import getproxy
class baseocr: 
    def langmap(self):
        return {}
    def initocr(self):
        pass
    def ocr(self,imgpath):
        raise Exception 
    def end(self):
        pass
    ############################################################
    @property
    def proxy(self):
        if ('useproxy' not in  globalconfig['ocr'][self.typename]) or globalconfig['ocr'][self.typename]['useproxy']:
            return getproxy()
        else:
            return {'https':None,'http':None}
    @property
    def srclang(self):
        try:
            l=static_data["language_list_translator_inner"][globalconfig['srclang3']]
            return self.langmap_[l] 
        except:
            return ''
    @property
    def space(self):
        if globalconfig['ocrmergelines']==False:
            space='\n'
        elif self.srclang in ['zh','ja','cht']:
            space=''
        else:
            space=' '
        return space 
    @property
    def config(self):
        try:
            return stripwrapper(ocrsetting[self.typename]['args'])
        except:
            return {}
    def countnum(self):
        try: 
            ocrsetting[self.typename]['args']['次数统计']=str(int(self.config['次数统计'])+1)
        except: 
            ocrsetting[self.typename]['args']['次数统计']='1'
        
    def checkempty(self,items):
        emptys=[]
        for item in items:
            if (self.config[item])=='':
                emptys.append(item)
        if len(emptys):
            raise ArgsEmptyExc(emptys)
            
    ############################################################
    def __init__(self,typename ) :  
        self.typename=typename 
        try: 
            self.initocr() 
        except Exception as e:
            raise e
    @property
    def langmap_(self):
        _=dict(zip(static_data["language_list_translator_inner"],static_data["language_list_translator_inner"]))
        _.update({'cht':'zh'})
        _.update(self.langmap())
        return _
     
    