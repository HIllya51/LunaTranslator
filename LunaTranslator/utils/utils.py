def argsort(l):
    ll=list(range(len(l)))
    ll.sort(key= lambda x:l[x])
    return ll
import os

def selectdebugfile(path,openf=False):
    p=None
    if os.path.exists(os.path.join('./LunaTranslator',path)):
        p= os.path.abspath(os.path.join('./LunaTranslator',path))
    elif os.path.exists(path):
        p= os.path.abspath(path)
    if p and openf:
        os.startfile(p)
    return p