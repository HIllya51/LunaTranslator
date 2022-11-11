 
import re
from traceback import print_exc
from typing import Counter
from collections import Counter

from utils.config import postprocessconfig 
def POSTSOLVE(line): 
    if line=="":
        return ""
    
    if postprocessconfig['_2']['use']:
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
    if postprocessconfig['_3']['use']:
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
         
    if postprocessconfig['_10']['use']:
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
    if postprocessconfig['_1']['use']:
        r=re.compile('\{(.*?)/.*?\}')
        line=r.sub(lambda x:x.groups()[0],line)
        r=re.compile('\{(.*?):.*?\}')
        line=r.sub(lambda x:x.groups()[0],line)
    if postprocessconfig['_4']['use']:  
        line =re.sub('<(.*?)>','',line) 
        line=re.sub('</(.*?)>',"*",line)
    if postprocessconfig['_6']['use']:
        line=line.replace('\n','').replace('\r','')
    if postprocessconfig['_9']['use']:
        line=re.sub('([0-9a-zA-Z]+)','',line)
    if postprocessconfig['_7']['use']:
        filters=postprocessconfig['_7']['args']['替换内容']
        for fil in filters: 
                if fil=="":
                        continue
                else:
                        line=line.replace(fil,filters[fil])
    if postprocessconfig['_8']['use']:
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