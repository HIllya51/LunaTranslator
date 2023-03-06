# coding: utf8
# inject.py
# 2/3/2013 jichi
# Windows only
import os
import platform
from utils.subproc import subproc2
def inject_vnragent(pid): 
  if platform.architecture()[0]=='64bit': 
      dllpaths=list(map(lambda x:os.path.abspath(os.path.join('./files/embedded5/',x)), ['Qt5Core.dll','Qt5Network.dll','vnragent.dll']))
  elif platform.architecture()[0]=='32bit':
      dllpaths=[os.path.abspath("./LunaTranslator/qt5core.dll"),os.path.abspath("./LunaTranslator/qt5network.dll"), os.path.abspath('./files/embedded5/vnragent.dll')] 
  
  print(f'.\\files\\embedded5\\dllinject32.exe {pid} "{dllpaths[0]}" "{dllpaths[1]}" "{dllpaths[2]}"')
  subproc2(f'.\\files\\embedded5\\dllinject32.exe {pid} "{dllpaths[0]}" "{dllpaths[1]}" "{dllpaths[2]}"')  
   