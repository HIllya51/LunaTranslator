 
from traceback import print_exc
import requests 
import threading 
import time,os
import threading
from threading import Lock 

from utils.utils import getproxy
from utils.config import globalconfig  
def mutithreaddownload(savep,url,progresscallback,internalsignal,endcallback):
        try:
            r2 = requests.get(url,stream=True,verify = False,proxies=getproxy()) 
            size = int(r2.headers['Content-Length'])
            if os.path.exists(savep):
                stats = os.stat(savep) 
                
                if stats.st_size==size:
                    progresscallback(f'总大小{int(1000*(int(size/1024)/1024))/1000} MB 进度 {int(10000*(size/size))/100:.2f}% ',10000)
                    endcallback()
                    return 
            with open(savep, "wb") as file:
                global file_size
                global sizecollect
                global sizecollecti
                global counter
                counter=0
                sizecollect=[]
                sizecollecti=0
                file_size=0 
                def download(start,end,sz):
                    headers = {
                        'Range': f'bytes={start}-{end}',
                    }
                    r = requests.get(url,stream=True,headers=headers,verify = False,proxies=getproxy()) 
                    pos = start
                    for i in r.iter_content(chunk_size=1024): 
                        if internalsignal()==False: 
                            return
                        if i: 
                            lock.acquire()  
                            file.seek(pos)
                            file.write(i)
                            global sizecollect
                            global sizecollecti
                            global file_size
                            global counter
                            thislen=len(i)
                            file_size+=thislen 
                            now=time.time()
                            sizecollect.append((now,thislen))
                            for i in range(sizecollecti,len(sizecollect)):
                                if now-sizecollect[i][0]<2:
                                    break
                                else:
                                    counter-=sizecollect[i][1]
                            sizecollecti=i
                            counter+=thislen
                            lock.release()   
                            speed=(counter/1024)/2
                            progresscallback(f'总大小{int(1000*(int(sz/1024)/1024))/1000} MB 进度 {int(10000*(file_size/sz))/100:.2f}% 速度 {speed:.2f}KB/s',int(10000*file_size/sz))
                            pos += 1024 
                
                lock = Lock() 
                thread_num =4
                
                ts=[]
                for i in range(thread_num):
                    if i == thread_num-1:
                        t1=threading.Thread(target=download,args=(i*(size//thread_num),size,size))
                        t1.start()
                        ts.append(t1)
                    else:
                        t1 = threading.Thread(target=download, args=(i*(size//thread_num), (i+1)*(size//thread_num),size))
                        t1.start()
                        ts.append(t1)
                for t in ts:
                    t.join()
                
            if internalsignal()==False: 
                return
            if os.path.exists(savep):
                stats = os.stat(savep) 
                
                if stats.st_size==size:
                    progresscallback(f'总大小{int(1000*(int(size/1024)/1024))/1000} MB 进度 {int(10000*(size/size))/100:.2f}% ',10000)
                    endcallback()
                    return  
            
        except:
            print_exc()
            progresscallback('自动更新失败，请手动更新',0)
