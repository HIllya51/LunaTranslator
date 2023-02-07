# coding: utf8
# engine.py
# 5/3/2014 jichi
# The logic in this file must be consistent with that in vnragent.dll.

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os
from glob import glob 
import re
class Engine:
  def __init__(self, name='', regionLocked=False, vnrboot=False, **kwargs):
    self.name = name # str
    self.regionLocked = regionLocked # bool
    self.vnrboot = vnrboot # bool

  # Not used
  #def encoding(self): return 'utf-16' if self.wideChar else 'shift-jis'
def escapeglob(path): # unicode -> unicode
  if '[' not in path:
    return path
  path = re.sub(r'\[', '[[]', path)
  path = re.sub(r'(?<!\[)\]', '[]]', path)
  return path
class EngineFinder:
  def __init__(self, pid=0, exepath='', dirpath=''):
    """
    @param* pid  long  process id
    @param* exepath  unicode  executable path
    @param* dirpath  unicode  process directory path
    """
     
    if not dirpath and exepath:
      dirpath = os.path.dirname(exepath)
    self.pid = pid # long
    self.exepath = exepath # unicode
    self.dirpath = dirpath # unicode
    #self.processName = skwin.get_process_name(pid)

  def eval(self, e):
    """
    @param  e  list or str
    @return  bool
    """
    if not e:
      return False
    if isinstance(e, list):
      for it in e:
        if not self.eval(it):
          return False
      return True
    # e is str or unicode
    elif '|' in e:
      for it in e.split('|'):
        if self.eval(it):
          return True
      return False
    elif e[0] == '!' and len(e) > 1:
      return not self.eval(e[1:])
    elif '*' in e:
      return self.globs(e)
    else:
      return self.exists(e)

  def globs(self, relpath):
    """
    @param  relpath  unicode
    @return  bool
    """
    return bool(self.dirpath and glob(os.path.join(escapeglob(self.dirpath), relpath)))

  def exists(self, relpath):
    """
    @param  relpath  unicode
    @return  bool
    """
    return bool(self.dirpath) and os.path.exists(os.path.join(self.dirpath, relpath))

  def getAbsPath(self, relpath):
    """
    @param  relpath  unicode
    @return  unicode
    """
    return os.path.join(self.dirpath, relpath)

# EOF
