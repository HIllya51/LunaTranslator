# coding: utf8
# sharedmem.py
# 5/8/2014 jichi
  
from textsource.embed.pyvnrmem3 import VnrSharedMemory
 
import win32utils
class VnrAgentSharedMemory:
  # Must be consistent with vnragent
  STATUS_EMPTY = 0
  STATUS_READY = 1
  STATUS_BUSY = 2
  STATUS_CANCEL = 3

  def __init__(self, parent=None):
    d = self.__d = VnrSharedMemory(parent)
    d.processId = 0 # long 
    d.index = 0 # int  current cell index

  def isAttached(self): return bool(self.__d.processId) and self.__d.isAttached()

  def attachProcess(self, pid): # long -> bool
    d = self.__d
    d.processId = pid
    key = 'vnragent.%s' % pid
    d.setKey(key)
    return d.attach(False) # readOnly = false

  def detachProcess(self, pid): # long -> bool
    d = self.__d
    ret = pid == d.processId and d.isAttached() and d.detach()
    if ret:
      d.processId = 0
      d.index = 0
    return ret

  def quit(self):
    d = self.__d
    if d.isAttached():
      self.setAllStatus(self.STATUS_CANCEL)
      d.detach()

  def notify(self, hash, role): # wakeup locks
    pid = self.__d.processId 
    if pid:
      # must be consistent with vnragent's config.h
      eventName = "vnragent.shmem.%s.%s.%s" % (pid, role, hash)
      eventName = eventName.replace('-', '_') # get rid of minus sign 
      ev = win32utils.CreateEvent( False, False, eventName) # initial state = False. True does NOT work 
      win32utils.SetEvent(ev)
      win32utils.CloseHandle(ev)

  # Set without checking if attached
  def setAllStatus(self, v):
    d = self.__d
    #if d.isAttached():
    d.setDataStatus(0, v)
 
  # Write-only
  def setDataStatus(self, i, v): self.__d.setDataStatus(i, v)
  def setDataHash(self, i, v): self.__d.setDataHash(i, v)
  def setDataRole(self, i, v): self.__d.setDataRole(i, v)
  def setDataText(self, i, v): self.__d.setDataText(i, v)
  def setDataLanguage(self, i, v): self.__d.setDataLanguage(i, v) 

# EOF
