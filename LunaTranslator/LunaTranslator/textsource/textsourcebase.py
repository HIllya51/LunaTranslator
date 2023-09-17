import threading ,hashlib,queue
import time,sqlite3,json,os,codecs,win32utils
from traceback import print_exc
from myutils.config import globalconfig,savehook_new_data
from myutils.utils import getfilemd5
class basetext:
    def __init__(self,textgetmethod,md5,prefix)  :  
        self.textgetmethod=textgetmethod  
        self.ending=False
        self.md5,self.prefix=md5,prefix
        self.sqlqueue=queue.Queue()
        if 'hwnd' not in dir(self):
            self.hwnd=0
        if 'pids' not in dir(self):
            self.pids=[]
        #self.sqlfname='./transkiroku/'+self.prefix+'.sqlite'
        self.sqlfname_all='./translation_record/'+self.prefix+'.pretrans_common.sqlite'
        
        try:
            
            # self.sqlwrite=sqlite3.connect(self.sqlfname,check_same_thread = False, isolation_level=None)
            self.sqlwrite2=sqlite3.connect(self.sqlfname_all,check_same_thread = False, isolation_level=None)
            # try:
            #     self.sqlwrite.execute('CREATE TABLE artificialtrans(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT,machineTrans TEXT,userTrans TEXT);')
            # except:
            #     pass
            try:
                self.sqlwrite2.execute('CREATE TABLE artificialtrans(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT,machineTrans TEXT);')
            except:
                pass
        except:
            print_exc
        threading.Thread(target= self.sqlitethread).start()
        threading.Thread(target=self.gettextthread_).start() 
    def sqlqueueput(self,xx):
        try:
            self.sqlqueue.put(xx)
        except:
            pass
     
    
    def sqlitethread(self):
        while True:
            task=self.sqlqueue.get()
            try:
                if len(task)==1: 
                    src,=task
                    lensrc=len(src)
                    ret=self.sqlwrite2.execute('SELECT * FROM artificialtrans WHERE source = ?',(src,)).fetchone()
                    try: 
                        savehook_new_data[self.pname]['statistic_wordcount']+=lensrc
                    except:
                        pass
                    if ret is None:
                        self.sqlwrite2.execute('INSERT INTO artificialtrans VALUES(NULL,?,?);',(src,json.dumps({})))

                        try: 
                            savehook_new_data[self.pname]['statistic_wordcount_nodump']+=lensrc
                        except:
                            pass
                elif len(task)==3:
                    src,clsname,trans=task  
                    ret=self.sqlwrite2.execute('SELECT machineTrans FROM artificialtrans WHERE source = ?',(src,)).fetchone()  
                     
                    ret=json.loads( (ret[0]) )
                    ret[clsname]=trans
                    ret=json.dumps(ret)  
                    self.sqlwrite2.execute('UPDATE artificialtrans SET machineTrans = ? WHERE source = ?',(ret,src))
            except:
                print_exc()
    
    def checkmd5prefix(self,pname):
        md5=getfilemd5(pname)
        prefix= md5+'_'+os.path.basename(pname).replace('.'+os.path.basename(pname).split('.')[-1],'') 
        return md5,prefix
    def gettextthread_(self):
        while True:
            if self.ending: 
                break 
            if globalconfig['autorun']==False  :
                time.sleep(0.1)
                continue

            #print(globalconfig['autorun'])
            try:
                t=self.gettextthread()
                if t and globalconfig['autorun']:
                    if type(t) ==tuple:
                        self.textgetmethod(*t) 
                    else:
                        self.textgetmethod(t)
            except: 
                print_exc() 
            
    def gettextthread(self):
        pass
    def runonce(self):
        pass
    def end(self):
        self.ending=True
        try:
            self.sqlwrite2.close()
        except:
            print_exc()