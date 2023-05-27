# coding: utf8
# sharedmem.py
# 5/8/2014 jichi
  
from ctypes import cast,POINTER,c_int,Structure,c_wchar_p,c_wchar,c_char,c_char_p,c_uint64,sizeof

class Cell(Structure):
  _fields_=[
     ('connect',c_uint64),
    ('status',c_uint64),
    ('hash',c_uint64),
    ('role',c_uint64),
    ('language',c_char*4),
    ('textSize',c_int),
    ('text',c_wchar*4000)
  ]
#print(sizeof(Cell))
import win32utils,mmap

class winsharedmem:
  # Must be consistent with vnragent
  STATUS_EMPTY = 0
  STATUS_READY = 1
  STATUS_BUSY = 2
  STATUS_CANCEL = 3

  def __init__(self, parent=None): 
    self.processId = 0 # long 
    self.index = 0 # int  current cell index
    

  def isAttached(self): return bool(self.processId)  

  def attachProcess(self, pid): # long -> bool
    d = self
    d.processId = pid
    
    fmap1=win32utils.OpenFileMapping(win32utils.FILE_MAP_READ|0x2,False,'LUNASHAREDMEM'+str(pid))
    address1=win32utils.MapViewOfFile(fmap1, win32utils.FILE_MAP_READ|0x2,  4096)
    print(address1)
    self.sharedcell=cast(address1,POINTER(Cell)) 
    self.sharedcell.contents.connect=1
     
    return True

  def detachProcess(self, pid): # long -> bool
    self.processId = 0
    self.index = 0
    self.sharedcell.contents.connect=0
    return True

  def quit(self): 
    if self.isAttached():
      self.setAllStatus(self.STATUS_CANCEL) 
      self.sharedcell.contents.connect=0
   
  def notify(self, hash, role): # wakeup locks
    pid = self.processId 
    if pid:
      # must be consistent with vnragent's config.h
      eventName = "LUNA_NOTIFY.%s.%s.%s" % (pid, role, hash)
      eventName = eventName.replace('-', '_') # get rid of minus sign 
      ev = win32utils.CreateEvent( False, False, eventName) # initial state = False. True does NOT work 
      win32utils.SetEvent(ev)
      win32utils.CloseHandle(ev)

  # Set without checking if attached
  def setAllStatus(self, v):
    d = self
    #if d.isAttached():
    d.setDataStatus(0, v)
 
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
        self.sharedcell.contents.hash=v
  def setDataStatus(self,i,v ):  
        self.sharedcell.contents.status=v 
  def setDataRole(self,i,v):
      self.sharedcell.contents.role=v
  def setDataLanguage(self,i,v):
      
      v=v.encode('ascii')
      self.sharedcell.contents.language=v 
  def setDataText(self,i,v): 
      self.sharedcell.contents.textSize=len(v.encode('utf-16-le'))
      self.sharedcell.contents.text=v 
            

# EOF
