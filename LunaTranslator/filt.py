import os
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

    try:
        x[1].encode('latin-1')
        hide=True
        cntl+=1
    except:
        pass

    try:
        x[1].encode('shift-jis')
    except:
        hide=True
        cntj+=1
    if os.path.isdir(x[1]) or os.path.isfile(x[1]):
        hide=True
        print(x)
    if hide==False:
        #print(x)
        cnts+=1

print(cnt,cnts,cntb,cntl,cntj)