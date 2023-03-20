# coding: utf8
# inject.py
# 2/3/2013 jichi
# Windows only
import os
import platform
from utils.subproc import subproc_w
def inject_vnragent(pid): 
  if platform.architecture()[0]=='64bit': 
      dllpaths=list(map(lambda x:os.path.abspath(os.path.join('./files/plugins/EmbededEngine/',x)), ['Qt5Core.dll','Qt5Network.dll','vnragent.dll']))
  elif platform.architecture()[0]=='32bit':
      dllpaths=[os.path.abspath("./LunaTranslator/qt5core.dll"),os.path.abspath("./LunaTranslator/qt5network.dll"), os.path.abspath('./files/plugins/EmbededEngine/vnragent.dll')] 
   
  subproc_w(f'.\\files\\plugins\\EmbededEngine\\dllinject32.exe {pid} "{dllpaths[0]}" "{dllpaths[1]}" "{dllpaths[2]}"')  
   