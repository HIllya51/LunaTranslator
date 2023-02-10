def argsort(l):
    ll=list(range(len(l)))
    ll.sort(key= lambda x:l[x])
    return ll
import os

def selectdebugfile(path ):
    p=None
    if os.path.exists(os.path.join('./LunaTranslator',path)):
        p= os.path.abspath(os.path.join('./LunaTranslator',path)) 
    if p  :
        os.startfile(p)
    return p