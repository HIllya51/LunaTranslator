from utils.config import globalconfig
import winsharedutils
import os
from traceback import print_exc
class hira:
    def __init__(self) -> None: 
        hirasettingbase=globalconfig['hirasetting']
    
        mecabpath=hirasettingbase['mecab']['path']
        if os.path.exists(mecabpath):
            self.kks=winsharedutils.mecab_init(mecabpath)#  fugashi.Tagger('-r nul -d "{}" -Owakati'.format(mecabpath))
            self.kanaindx=winsharedutils.mecab_getkanaindex(self.kks)
            keys='ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ'
            vs='ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ'
            self.h2k=str.maketrans( keys,vs)
         
 
    def fy(self,text): 
            start=0
            result=[] 
            for node,fields in winsharedutils.mecab_parse(self.kks,text):# self.kks.parseToNodeList(text): 
                if len(fields):
                    pos1=fields[0]
                    if (self.kanaindx>0)and (self.kanaindx<=len(fields)-1):
                        kana=fields[self.kanaindx]
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
     