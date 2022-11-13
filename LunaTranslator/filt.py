import os
import chardet
with open('hook.txt','r',encoding='utf8') as ff:
    ls=ff.read().split('\n')
cnt=0
cntl=0
cntj=0
cntb=0
cnts=0
for l in ls:
    
    x=l.split('=>')
    if len(x)!=2:
        continue
    cnt+=1
    hide=False
    if x[1].strip()=='':
        hide=True
        cntb+=1
    print(chardet.detect(x[1].encode('utf8')),x[1])
     

print(cnt,cnts,cntb,cntl,cntj)