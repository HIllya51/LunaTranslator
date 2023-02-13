# coding: utf8
# inject.py
# 2/3/2013 jichi
# Windows only
import os
from utils.subproc import subproc
def inject_vnragent(pid): 
  ret = True
  for dllpath in os.listdir('./files/embedded5'):
    if dllpath[-4:]!='.dll':
      continue
    dllpath='./files/embedded5/'+dllpath
    dllpath = os.path.abspath(dllpath)
    
    print('.\\files\\embedded5\\dllinject32.exe '+str(pid)+' "'+dllpath+'"')
    subproc('.\\files\\embedded5\\dllinject32.exe '+str(pid)+' "'+dllpath+'"')  
  return ret
