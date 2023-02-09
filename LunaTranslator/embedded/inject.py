# coding: utf8
# inject.py
# 2/3/2013 jichi
# Windows only
import os
from utils.subproc import subproc
def inject_vnragent(pid): 
  ret = True
  for dllpath in os.listdir('./files/embedded'):
    if dllpath[-4:]!='.dll':
      continue
    dllpath='./files/embedded/'+dllpath
    dllpath = os.path.abspath(dllpath)
    
    print('.\\files\\embedded\\dllinject32.exe '+str(pid)+' "'+dllpath+'"')
    subproc('.\\files\\embedded\\dllinject32.exe '+str(pid)+' "'+dllpath+'"')  
  return ret
