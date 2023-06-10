from myutils.config import globalconfig
import winsharedutils
import os
from traceback import print_exc
_cache={}
class hira:
    def __init__(self) -> None: 
        hirasettingbase=globalconfig['hirasetting']
    
        mecabpath=hirasettingbase['mecab']['path']
        if os.path.exists(mecabpath):
            self.kks=winsharedutils.mecab_init(mecabpath)#  fugashi.Tagger('-r nul -d "{}" -Owakati'.format(mecabpath))
            if self.kks is None:    #32位下重新init会失败，不明白为什么。
                if mecabpath in _cache: 
                    self.kks=_cache[mecabpath]
            else:
                _cache[mecabpath]=self.kks
            keys='ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ'
            vs='ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ'
            self.h2k=str.maketrans( keys,vs)
         
 
    def fy(self,text): 
            start=0
            result=[] 
            for node,fields in winsharedutils.mecab_parse(self.kks,text):# self.kks.parseToNodeList(text): 
                if len(fields):
                    pos1=fields[0] 
                    if len(fields)>29:
                        kana=fields[22]
                    elif len(fields)==29:
                        kana=fields[20]
                    elif 29>len(fields)>=26:
                        kana=fields[17]
                    elif len(fields)>9:
                        kana=fields[9] #无kana，用lform代替
                    else:
                        kana=''
                else:
                    kana=''
                    pos1=''
                l=0
                if text[start]=='\n':
                    start+=1
                while str(node) not in text[start:start+l]:
                    l+=1
                orig=text[start:start+l]
                start+=l
                hira=kana.translate(self.h2k)
                
                if hira=='*':
                    hira=''
                #print(node.feature) 
                result.append({'orig':orig,"hira":hira,"cixing":pos1}) 
            return result
     