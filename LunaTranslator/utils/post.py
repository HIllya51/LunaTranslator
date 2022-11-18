 
import re
from traceback import print_exc
from typing import Counter
from collections import Counter
import importlib
from utils.config import postprocessconfig,globalconfig 
def _2_f(line):
        times=postprocessconfig['_2']['args']['重复次数(若为1则自动分析去重)']
         
        if times>=2:
                guesstimes=times
        else :
                guesstimes=[]
                t1=1
                for i in range(1,len(line)):
                        if line[i]==line[i-1]:

                                t1+=1
                        else:
                                
                                guesstimes.append(t1)
                                t1=1
                x=Counter(guesstimes)
              
                if len(guesstimes)!=0:
                        guesstimes=sorted(x.keys(),key= lambda x1:x[x1])[-1]
                else:
                        guesstimes=1
        
        newline=[line[i*guesstimes] for i in range(len(line)//guesstimes)]
        line=''.join(newline)
        return line
def _3_f(line):
        times=postprocessconfig['_3']['args']['重复次数(若为1则自动分析去重)']
         
        if times>=2:
                guesstimes=times
        else :
                guesstimes=len(line) 
                while guesstimes>=1:
                        if line[:len(line)//guesstimes]*guesstimes==line: 
                                break
                        guesstimes-=1
        line=line[:len(line)//guesstimes] 
        return line
def _10_f(line):
        cnt=Counter(line)
        saveline=[]
        for k in sorted(cnt.keys(),key= lambda x :-cnt[x]) :
                last=line.rfind(k)

                length=1
                while True:
                        if last-length<0:
                          break
                        
                        if line[last]==line[last-length]:
                          last=last-length
                        if last-length>0:
                                length+=1
                        else:
                                break
                saveline.append(line[last-length:last+1])
         
        line=sorted(saveline, key=len, reverse=True)[0]
        return line
def _1_f(line):
        r=re.compile('\{(.*?)/.*?\}')
        line=r.sub(lambda x:x.groups()[0],line)
        r=re.compile('\{(.*?):.*?\}')
        line=r.sub(lambda x:x.groups()[0],line)
        return line
def _4_f(line):
        line =re.sub('<(.*?)>','',line) 
        line=re.sub('</(.*?)>',"*",line)
        return line
def _6_f(line):
        line=line.replace('\n','').replace('\r','')
        return line
def _9_f(line):
        line=re.sub('([0-9a-zA-Z]+)','',line)
        return line
def _7_f(line):
        filters=postprocessconfig['_7']['args']['替换内容']
        for fil in filters: 
                if fil=="":
                        continue
                else:
                        line=line.replace(fil,filters[fil])
        return line
def _8_f(line):
        filters=postprocessconfig['_8']['args']['替换内容'] 
        for fil in filters: 
                if fil=="":
                        continue
                else:  
                        try:
                                line=re.sub(fil,filters[fil],line)
                        except:
                                print_exc()
        return line

def POSTSOLVE(line): 
    if line=="":
        return ""
    functions={
        '_2':_2_f,
        '_3':_3_f,
        '_10':_10_f,
        '_1':_1_f,
        '_4':_4_f,
        '_6':_6_f,
        '_9':_9_f,
        '_7':_7_f,
        '_8':_8_f,
        '_11':importlib.import_module('postprocess.mypost').POSTSOLVE
    }
    for postitem in globalconfig['postprocess_rank']:
        if postprocessconfig[postitem]['use']:
                try:
                        line=functions[postitem](line)
                except:
                        pass 
        
    return line