import requests,os
from translator.basetranslator import basetrans  
from myutils.subproc import subproc_w,autoproc
class TS(basetrans):   
    def inittranslator(self):
        checks=['Runtime','tokenizator','translator']
        self.checkempty(checks)

        self.Port=self.config['Port']
        server=os.path.join(self.config['Runtime'],'server.py')
        pyexe=os.path.join(self.config['Runtime'],'python-3.11.8-embed-amd64/python.exe')
        for k in [self.config[k] for k in checks]+[server,pyexe]:
            if os.path.exists(k)==False:
                raise Exception('not exists:'+k)
        
        
        self.engine=autoproc(subproc_w('"{}" "{}" "{}" "{}" {}'.format(pyexe,server,self.config['translator'],self.config['tokenizator'],self.Port),name='sugoi'))
    def translate(self,query):  
        return (requests.get('http://127.0.0.1:{}/translate'.format(self.Port),params={'text':query}).json())['trans']