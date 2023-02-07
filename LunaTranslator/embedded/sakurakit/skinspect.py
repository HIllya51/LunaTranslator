# coding: utf8
# skinspect.py
# 3/26/2013 jichi
# See: http://stackoverflow.com/questions/5863512/python-how-to-get-the-class-of-a-calling-method-through-inspection

import inspect

# Indices of inspect.stack()[1]
CALLER_FRAME_INDEX = 0  # caller frame context
CALLER_FILE_INDEX = 1   # caller file path
CALLER_FUNC_INDEX  = 3  # caller function name

def get_func_name():
  """
  @return  str
  """
  caller = inspect.stack()[1] # caller object
  return caller[CALLER_FUNC_INDEX]

def get_class():
  """
  @return  class
  """
  caller = inspect.stack()[1] # caller object
  frame = caller[CALLER_FRAME_INDEX]

  try:
    self = frame.f_code.co_varnames[0]
    instance = frame.f_locals[self]
    return instance.__class__
  except (KeyError, IndexError, TypeError): pass

def get_class_name():
  """
  @return  str
  """
  caller = inspect.stack()[1] # caller object
  frame = caller[CALLER_FRAME_INDEX]

  try:
    self = frame.f_code.co_varnames[0]
    instance = frame.f_locals[self]
    return instance.__class__.__name__
  except (KeyError, IndexError, TypeError): pass

# EOF
