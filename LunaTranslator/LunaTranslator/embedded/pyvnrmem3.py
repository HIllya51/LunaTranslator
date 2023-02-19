
from  PyQt5.QtCore import QSharedMemory,QObject 
LanguageCapacity=4  
        # _fields_=[
        #     ('status',c_int8),  #8
        #     ('hash',c_int64),   #8
        #     ('role',c_int8),    #1
        #     ('language',c_char*LanguageCapacity), #8
        #     ('textSize',c_int32),#4
        #     ('text',c_wchar_p) 
        # ]
class VnrSharedMemory(QObject):
     
    def __init__(self,p=None ) :
        super(VnrSharedMemory,self).__init__() 
        self.cellCount_=0
        self.cellSize_=0   
        self.memory=QSharedMemory()
      
    def setKey(self,v):
        self.memory.setKey(v)
     
    def attach(self,readOnly):
        return self.memory.attach(QSharedMemory.ReadOnly if readOnly else QSharedMemory.ReadWrite)
    def detach(self):
        return self.memory.detach()
    def isAttached(self):
        return self.memory.isAttached() 
    def packuint(self,i, size=0): # int -> str
        """
        @param  i  int
        @param* size  int  total size after padding
        @return  str
        """
        if i<0:
            i=(2**(8*size))+i
        r = ''
        while i:
            r = r+chr(i & 0xff) 
            i = i >> 8
        while len(r) < size:
            r = r+chr(0) 
        return r
    def setDataHash(self,i,v ): 
        v=self.packuint(v,8) 
        mv=memoryview(self.memory.data()) 
        for i in range(8):
            mv[i+8]=ord(v[i]  )
    
    def setDataStatus(self,i,v ):  
        v=self.packuint(v,8) 
        mv=memoryview(self.memory.data()) 
        for i in range(8):
            mv[i]=ord(v[i])   
    def setDataRole(self,i,v):
        v=self.packuint(v,1) 
        mv=memoryview(self.memory.data()) 
        mv[16]=ord(v[0])   
    def setDataLanguage(self,i,v):
        
        v=v.encode('ascii')
        mv=memoryview(self.memory.data()) 
        for i in range(min(8,len(v))):
            mv[i+17]= (v[i] ) 
    def setDataText(self,i,v): 
        l=len(v)
        uv=v.encode('utf-16-le') 
        v=self.packuint(l,4)
        mv=memoryview(self.memory.data()) 
        for i in range(4):
            mv[i+24]=ord(v[i] )

        for i in range(len(uv)):
            mv[i+28]= (uv[i])
             