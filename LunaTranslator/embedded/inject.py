# coding: utf8
# inject.py
# 2/3/2013 jichi
# Windows only
import os
def inject_vnragent(pid): 
  ret = True
  for dllpath in ['msvcr100.dll',
                  'msvcp100.dll',
                  'qtcore4.dll',
                  'qtnetwork4.dll',
                  'vnragent']:
    
    #dllpath = os.path.abspath(dllpath)
    dllpath = os.path.abspath(dllpath)   
    os.system('dllinject32.exe '+str(pid)+' "'+dllpath+'"') 
    print('dllinject32.exe '+str(pid)+' "'+dllpath+'"')
  return ret
