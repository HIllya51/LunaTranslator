
import re

def POSTSOLVE(line): 
        r=re.compile('\{(.*?)/.*?\}')
        line=r.sub(lambda x:x.groups()[0],line)
        return line