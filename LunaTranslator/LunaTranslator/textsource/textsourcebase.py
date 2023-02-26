import threading ,hashlib,queue
import time,sqlite3,json,os,codecs
from traceback import print_exc
from utils.config import globalconfig
class basetext:
    def __init__(self,textgetmethod,md5,prefix)  :  
        self.textgetmethod=textgetmethod  
        self.ending=False
        self.md5,self.prefix=md5,prefix
        self.sqlqueue=queue.Queue()
        self.t=threading.Thread(target=self.gettextthread_)
        self.t.setDaemon(True)
        self.t.start()
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
    def put(self,xx):
        try:
            self.sqlqueue.put(xx)
        except:
            pass
    def quote_identifier(self,s, errors="strict"):
        encodable = s.encode("utf-8", errors).decode("utf-8")

        nul_index = encodable.find("\x00")

        if nul_index >= 0:
            error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                    nul_index, nul_index + 1, "NUL not allowed")
            error_handler = codecs.lookup_error(errors)
            replacement, _ = error_handler(error)
            encodable = encodable.replace("\x00", replacement)

        return "\"" + encodable.replace("\"", "\"\"") + "\""
    def unpack(self,s):
        s=s[1:-1]

        return s.replace( "\"\"","\"") 
    def sqlitethread(self):
        while True:
            task=self.sqlqueue.get()
            try:
                if len(task)==1:
                    src,=task
                    src=self.quote_identifier(src )
                    ret=self.sqlwrite2.execute(f'SELECT * FROM artificialtrans WHERE source = {src}').fetchone()
                    if ret is None:
                        null=self.quote_identifier(json.dumps({}))
                        self.sqlwrite2.execute(f'INSERT INTO artificialtrans VALUES(NULL,{src},{null});')
                elif len(task)==3:
                    src,clsname,trans=task 
                    src=self.quote_identifier(src) 
                    
                    ret=self.sqlwrite2.execute(f'SELECT machineTrans FROM artificialtrans WHERE source = {src}').fetchone()  
                     
                    ret=json.loads( (ret[0]) )
                    ret[clsname]=trans
                    ret=json.dumps(ret)  
                    ret=self.quote_identifier(ret)
                    self.sqlwrite2.execute(f'UPDATE artificialtrans SET machineTrans = {ret} WHERE source = {src}')
            except:
                print_exc()
    
    def checkmd5prefix(self,pname):
        with open(pname,'rb') as ff:
            bs=ff.read() 
        md5=hashlib.md5(bs).hexdigest()
        prefix= md5+'_'+os.path.basename(pname).replace('.'+os.path.basename(pname).split('.')[-1],'') 
        return md5,prefix
    def gettextthread_(self):
        while True:
            if self.ending: 
                break 
            if globalconfig['autorun']==False  :
                self.ignoretext()
                time.sleep(0.1)
                continue

            #print(globalconfig['autorun'])
            try:
                t=self.gettextthread()
                if t and globalconfig['autorun']:
                    self.textgetmethod(t) 
                    
            except: 
                print_exc() 
            
            
    def ignoretext(self):
        pass
    def gettextthread(self):
        pass
    def runonce(self):
        pass
    def end(self):
        self.ending=True
 