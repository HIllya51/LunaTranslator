import time
import win32pipe,win32file,win32con
def ocr(imgfile,lang): 
    timestamp=imgfile[10:-4]
    t1=time.time()
    win32pipe.WaitNamedPipe("\\\\.\\Pipe\\ocrwaitsignal_"+timestamp,win32con.NMPWAIT_WAIT_FOREVER)
    hPipe = win32file.CreateFile( "\\\\.\\Pipe\\ocrwaitsignal_"+timestamp, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
            None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
    #win32file.WriteFile(hPipe,'haha'.encode('utf8'))
    s=(win32file.ReadFile(hPipe, 65535, None)[1].decode('utf8'))
    ls=s.split('\n')[:-1] 
    juhe=[]
    box=[]
    mids=[]
    ranges=[]
    text=[]
    reverse={}
    for i in range(len(ls)//2):
        box.append([int(_)  for _ in ls[i*2].split(',')])
        text.append(ls[i*2+1]) 
    for i in range(len(box)):
        mid=box[i][1]+box[i][3]+box[i][5]+box[i][7]
        mid/=4
        mids.append(mid)
        range_=((box[i][1]+box[i][3])/2,(box[i][7]+box[i][5])/2)
        ranges.append(range_) 
    passed=[] 
    for i in range(len(box)):
        ls=[i]
        if i in passed:
            continue
        for j in range(i+1,len(box)):
            if j in passed:
                continue 
            if mids[i]>ranges[j][0] and mids[i]<ranges[j][1] \
                and mids[j]>ranges[i][0] and mids[j]<ranges[i][1]:
                    
                passed.append(j)
                ls.append(j)
        juhe.append(ls)
    
    for i in range(len(juhe)):
        juhe[i].sort(key=lambda x:box[x][0])
    juhe.sort(key=lambda x:box[x[0]][1])
    lines=[]
    for _j in juhe:
            
        lines.append(''.join([text[_] for _ in _j])) 

    return ''.join(lines)