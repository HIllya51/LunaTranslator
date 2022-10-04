from logging import Filterer
import re
from typing import Counter

from utils.config import postprocessconfig 
def POSTSOLVE(line): 
    if line=="":
        return ""
    if postprocessconfig['_1']['use']:
        r=re.compile('\{(.*?)/.*?\}')
        line=r.sub(lambda x:x.groups()[0],line)
    if postprocessconfig['_2']['use']:
        times=postprocessconfig['_2']['args']['重复次数']
         
        if times>=1:
                guesstimes=times
        elif times==0:
                guesstimes=[]
                t1=1
                for i in range(1,len(line)):
                        if line[i]==line[i-1]:

                                t1+=1
                        else:
                                
                                guesstimes.append(t1)
                                t1=1
                x=Counter(guesstimes)
                guesstimes=sorted(x.keys(),key= lambda x1:x[x1])[-1]
        
        newline=[line[i*guesstimes] for i in range(len(line)//guesstimes)]
        line=''.join(newline)
    if postprocessconfig['_3']['use']:
        testforlongestnotdup=line
        time=2
        while time<len(line):
                if line[:len(line)//time]*time==line:
                        testforlongestnotdup=line[:len(line)//time]
                else:
                        break
                time+=1
        line=testforlongestnotdup 
    if postprocessconfig['_4']['use']:  
        line =re.sub('<(.*?)>','',line) 
        line=re.sub('</(.*?)>',"*",line)
    if postprocessconfig['_6']['use']:
        line=line.replace('\n','')
    if postprocessconfig['_5']['use']:
        filters=postprocessconfig['_5']['args']['过滤内容']
        for fil in filters: 
                if fil=="":
                        continue
                else:
                        line=line.replace(fil,'')
    return line