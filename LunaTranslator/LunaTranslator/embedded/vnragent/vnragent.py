# coding: utf8
# vnragent.py
# 5/3/2014 jichi
# The logic in this file must be consistent with that in vnragent.dll.

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")
 

#ENGINE_YAML = os.path.join(os.path.dirname(__file__), 'engines.yaml')
ENGINE_json ='./files/embedded/engines.json'

# TODO: Apply this transformation for all paths at Python side
def _complete_path(path):
  """Repair remote path by padding leading '\\'
  @param  path  unicode
  @return  unicode  path
  """
  if path and len(path) > 2 and path[0] == '\\' and path[1] != '\\':
    path = '\\' + path
  return path
 
import win32api,win32con,win32process
def get_engine_data():
  import json
  return json.load(file(ENGINE_json, 'r'))
def get_process_path(pid):
    """
    @param  pid  long
    @return  unicode or ""
    """
    path = ""
    try:
      h = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
      if h:
        # This function returns WCHAR
        path = win32process.GetModuleFileNameEx(h, 0)
        win32api.CloseHandle(h)
    except Exception  as e: print(e)
    return path
def match(pid=0, path=None):
  """
  @param* pid  long
  @param* path  unicode  file executable
  @return  Engine or None
  """
  if not path and pid:
      path =  get_process_path(pid)
  from  embedded.vnragent.engine import Engine, EngineFinder
  path = _complete_path(path)
  print("match pid path",path)
  finder = EngineFinder(pid=pid, exepath=path)
  for eng in get_engine_data():
    if finder.eval(eng['exist']): #or True:
      print("engine = %s" % eng['name'])
      return Engine(**eng)
  print("matching engine")
  from  embedded.vnragent import engines
  for eng in engines.ENGINES:
    if eng.match(finder):
      print("engine = %s" % eng.name)
      return Engine(name=eng.name)

# EOF
