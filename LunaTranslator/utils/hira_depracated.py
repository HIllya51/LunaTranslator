from utils.config import globalconfig

import os
from traceback import print_exc
class hira:
    def __init__(self) -> None: 
        hirasettingbase=globalconfig['hirasetting']
        if hirasettingbase['mecab']['use']:
            mecabpath=hirasettingbase['mecab']['path']
            if os.path.exists(mecabpath):
                import fugashi 
                self.kks= fugashi.Tagger('-r nul -d "{}" -Owakati'.format(mecabpath))
                self.usemecab=True
                keys='ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ'
                vs='ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ'
                self.h2k=str.maketrans( keys,vs)
        elif hirasettingbase['local']['use']:
            import pykakasi
            self.kks = pykakasi . kakasi ()
            self.usemecab=False
         
                
    def guesslen(self,text):
        lenl=0
        for s in text:
            if ord(s)<=128 or s in ['“”…']:
                lenl+=1
            else:
                lenl+=2
        return lenl
    def search(self,text ):
        
        text,line,idx=text 
        if self.usemecab: 
            if line:
                x=self.kks.parseToNodeList(line)
                node=x[idx]
                try:
                    xx=str(node)
                    if node.feature.kana:
                        xx+='-'+node.feature.kana.translate(self.h2k)

                    xx+=f'<br>词性：'
                    if node.feature.pos1!='*':
                        xx+=f'{node.feature.pos1}'
                    if node.feature.pos2!='*':
                        xx+=f'-{node.feature.pos2}' 
                    if node.feature.pos3!='*':
                        xx+=f'-{node.feature.pos3}' 
                    if node.feature.pos4!='*':
                        xx+=f'-{node.feature.pos4}' 
                    if node.feature.cType!='*':
                        xx+=f'<br>{node.feature.cType}'
                    if node.feature.cForm!='*':
                        xx+=f'<br>{node.feature.cForm}' 
                    if node.feature.orthBase:
                        xx+=f'<br>词根：{node.feature.orthBase}'
                    return xx
                except:
                    return ''
            res=[] 
            for node in self.kks.parseToNodeList(text):
                #print(node.feature)
                try:
                    xx=str(node)+'-'+node.feature.kana.translate(self.h2k)

                    xx+=f'<br>词性：'
                    if node.feature.pos1!='*':
                        xx+=f'{node.feature.pos1}'
                    if node.feature.pos2!='*':
                        xx+=f'-{node.feature.pos2}' 
                    if node.feature.pos3!='*':
                        xx+=f'-{node.feature.pos3}' 
                    if node.feature.pos4!='*':
                        xx+=f'-{node.feature.pos4}' 
                    if node.feature.cType!='*':
                        xx+=f'<br>{node.feature.cType}'
                    if node.feature.cForm!='*':
                        xx+=f'<br>{node.feature.cForm}' 
                    xx+=f'<br>词根：{node.feature.orthBase}'
                    res.append(xx)
                except:
                    pass
            return '<hr>'.join(res)
        else:
            res=[]
            xx=self.kks . convert ( text )
            for x in xx:
                res.append(x['orig']+'-'+x['hira'])
            return '<hr>'.join(res)
    def fy(self,text): 
        if self.usemecab:
            start=0
            result=[] 
            for node in self.kks.parseToNodeList(text): 
                l=0
                if text[start]=='\n':
                    start+=1
                while str(node) not in text[start:start+l]:
                    l+=1
                orig=text[start:start+l]
                start+=l
                try:
                    hira=node.feature.kana.translate(self.h2k)
                except:
                    hira=''
                #print(node.feature)
                result.append({'orig':orig,"hira":hira,"cixing":node.feature.pos1}) 
        else:
            result =self.kks . convert ( text )
        return result
    def fy_depracated(self,text): 
        
        sp=text.split('\n')
        nsp=[]
        for s in sp:
            if len(s)>0:
                nsp.append(s)
        text='\n'.join(nsp)
        if text=='':
            return 
        result =self.kks . convert ( text )
        ss=''

        diff=0
        rawtext=''
        hiras=''
        hiralen=0
        rawlen=0
        alllen=0
        startandlen=[]
        for res in result:
            
            lenl=self.guesslen(res['orig'])
            startandlen.append([alllen,lenl])
            alllen+=lenl
        hiras=' '*alllen
        resss=[]
        hiraplace=[]
        resuse=[]
        guiuse=''
        for i,res in enumerate(result):
            guiuse+=res['orig']
            
            if res['orig']!=res['hira']:
                #print(res['orig'],res['hira'])
                if (set(res['orig']) -set(' \r\n'))==set():
                    continue
                guiuse+=f'({res["hira"]})'
                lenhira=self.guesslen(res['hira'])
                if lenhira==0:
                    continue
                start=startandlen[i][0]
                lenl=startandlen[i][1]
                mid=start+lenl//2
                ss=mid-lenhira//2
                end=mid+lenhira-lenhira//2
                resss.append(hiras[:ss]+res['hira']+hiras[end:])
                ##print(hiras[:ss]+res['hira']+hiras[end:])
                resuse.append(res['hira'])
                hiraplace.append(set([ss+i for i in range(lenhira)])) 
            
        line1=[]
        line2=[]
        ##print(hiraplace)
        for i in range(len(hiraplace)):
            bad=0
            for j in range(len(line1)):
                if len(hiraplace[i] & hiraplace[line1[j]] )>0: 
                    line2.append(i)
                    bad=1
            if bad==0:
                line1.append(i)
       # #print(line1,line2)
        hiratext1=''
        hiratext2=''
        colorswitch=0
        hiratextlen1=0
        hiratextlen2=0
        for i in range(len(hiraplace)):
            colorswitch+=1
            if i in line1:
                ##print(min(hiraplace[i]),self.guesslen(hiratext1))
                hiratext1+=' '*(min(hiraplace[i])-hiratextlen1)
                hiratextlen1+=self.guesslen(resuse[i]+' '*(min(hiraplace[i])-hiratextlen1))
                #hiratext1+='\033[0;'+str(31+colorswitch%4)+'m'+resuse[i]+'\033[0m'
                hiratext1+='\033[0;'+str(32+colorswitch%2)+'m'+resuse[i]+'\033[0m'
            else:
                hiratext2+=' '*(min(hiraplace[i])-hiratextlen2)
                hiratextlen2+=self.guesslen(resuse[i]+' '*(min(hiraplace[i])-hiratextlen2))
                #hiratext2+='\033[0;'+str(31+colorswitch%4)+'m'+resuse[i]+'\033[0m'
                hiratext2+='\033[0;'+str(32+colorswitch%2)+'m'+resuse[i]+'\033[0m'
        
        colorswitch=0
        for i,res in enumerate(result):
    
            if res['orig']!=res['hira']:
                lenhira=self.guesslen(res['hira'])
                start=startandlen[i][0]
                lenl=startandlen[i][1]
                mid=start+lenl//2
                ss=mid-lenhira//2
                end=mid+lenhira-lenhira//2
                resss.append(hiras[:ss]+res['hira']+hiras[end:]) 
                colorswitch+=1
                #rawtext+='\033[0;'+str(31+colorswitch%4)+'m'+res['orig']+'\033[0m'
                rawtext+='\033[0;'+str(42+colorswitch%2)+'m'+res['orig']+'\033[0m'
            else:
                rawtext+=res['orig']
        if True:#set(hiratext2)!=set(' ') and set(hiratext2)!=set(''):
            #print(hiratext2)
            pass
        if True:#set(hiratext1)!=set(' ') and set(hiratext1)!=set(''):
            #print(hiratext1)
            pass
        #print(rawtext)
        return hiratext2,hiratext1,rawtext,guiuse