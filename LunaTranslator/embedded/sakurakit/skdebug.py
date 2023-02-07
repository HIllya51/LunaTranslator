# coding: utf8
# skdebug.py
# 10/10/2012 jichi

from __future__ import print_function
import functools, inspect, os, sys 
from sakurakit import skinspect

DEBUG = True

## Functions ##

def safeprint(*args, **kwargs):
  try: print(*args, **kwargs)
  except Exception: pass

# See: http://stackoverflow.com/questions/5863512/python-how-to-get-the-class-of-a-calling-method-through-inspection
def dprint(msg, *args):
  if not DEBUG:
    return
  """Parameters are in the same format as print in Py3K"""
  caller = inspect.stack()[1] # caller object
  frame = caller[skinspect.CALLER_FRAME_INDEX]
  path = caller[skinspect.CALLER_FILE_INDEX]
  func = caller[skinspect.CALLER_FUNC_INDEX]

  try:
    self = frame.f_code.co_varnames[0]
    instance = frame.f_locals[self]
    class_ = instance.__class__.__name__
  except (KeyError, IndexError, TypeError):
    class_ = None # class name

  file_ = os.path.basename(path) # file name or module name
  if file_ == '__main__.py':
    file_ = os.path.basename(os.path.dirname(path))
    if func == '<module>':
      func = '__main__.py'
  if args:
    if class_:
      safeprint("%s:%s:%s:" % (file_,class_,func), msg, *args, file=sys.stderr)
    else:
      safeprint("%s:%s:" % (file_,func), msg, args, file=sys.stderr)
  else:
    if class_:
      safeprint("%s:%s:%s:" % (file_,class_,func), msg, file=sys.stderr)
    else:
      safeprint("%s:%s:" % (file_,func), msg, file=sys.stderr)

COLORAMA_INIT = False
def dwarn(msg, *args):
  return dprint(msg,args)
  