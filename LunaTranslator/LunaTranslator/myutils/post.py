 
import re,codecs
from traceback import print_exc
from collections import Counter
import importlib,gobject
from myutils.utils import getfilemd5
from myutils.config import postprocessconfig,globalconfig ,savehook_new_data,static_data
def _2_f(line,args):
        keepnodump=args['保持非重复字符']
        times=args['重复次数(若为1则自动分析去重)']
         
        if times>=2:
                guesstimes=times
        else :
                guesstimes=[]
                t1=1
                for i in range(1,len(line)):
                        if line[i]==line[i-1]:

                                t1+=1
                        else:
                                
                                guesstimes.append(t1)
                                t1=1
                x=Counter(guesstimes)
              
                if len(guesstimes)!=0:
                        guesstimes=sorted(x.keys(),key= lambda x1:x[x1])[-1]
                else:
                        guesstimes=1
        if keepnodump:
               newline=''
               i=0
               while i<len(line):
                      newline+=line[i]
                      nextn=line[i:i+guesstimes]
                      #print(guesstimes,nextn,len(set(nextn)))
                      if len(nextn)==guesstimes and len(set(nextn))==1:
                             i+=guesstimes
                      else:
                             i+=1  
               line=newline
        else:
                newline=[line[i*guesstimes] for i in range(len(line)//guesstimes)]
                line=''.join(newline)
        return line
def _3_f(line,args):
        times=args['重复次数(若为1则自动分析去重)']
         
        if times>=2:
                guesstimes=times
        else :
                guesstimes=len(line) 
                while guesstimes>=1:
                        if line[:len(line)//guesstimes]*guesstimes==line: 
                                break
                        guesstimes-=1
        line=line[:len(line)//guesstimes] 
        return line
def _3_2(line):
        cache=''
        
        

        while len(line):
                last=None
                dumplength=len(line)//2
                while dumplength>1:
                        bad=False
                        for i in range(dumplength):
                              _i=i+dumplength
                              if(line[i]!=line[_i]):
                                bad=True
                                break
                        if bad:
                          dumplength-=1
                        else:
                            current=line[:dumplength]
                            if last and last!=current:
                                cache+= current
                            last=current  
                            line=line[dumplength:]
                            break
                if last is None:
                       cache+=line[0]
                       line=line[1:]
 
        return cache
def _10_f(line):
        cnt=Counter(line)
        saveline=[]
        for k in sorted(cnt.keys(),key= lambda x :-cnt[x]) :
                last=line.rfind(k)

                length=1
                while True:
                        if last-length<0:
                          break
                        
                        if line[last]==line[last-length]:
                          last=last-length
                        if last-length>0:
                                length+=1
                        else:
                                break
                saveline.append(line[last-length:last+1])
         
        line=sorted(saveline, key=len, reverse=True)[0]
        return line
def _13_f(line): #递增式
        cnt=Counter(line)
        saveline=[]
        for k in sorted(cnt.keys(),key= lambda x :-cnt[x]) :
                 
                first=line.find(k)
                length=1
                while True:
                        if first+length>=len(line):
                          break
                        
                        if line[first]==line[first+length]:
                            first+=length
                        if first+length<len(line):
                               
                                length+=1
                        else:
                                break
                saveline.append(line[first:first+length])
         
        line=sorted(saveline, key=len, reverse=True)[0]
        return line
def _13_fEX(line:str): 
    saves=[]
    while len(line):
        for i in range(len(line)):
            maxlongline=line[i:]
            shengyu=line
            _maxlong=maxlongline
            succ=True
            while len(_maxlong):
                if shengyu.endswith(_maxlong)==False:
                    succ=False
                    break
                shengyu=shengyu[:-len(_maxlong)]
                _maxlong=_maxlong[:-1]
            if succ:break
        saves.append(maxlongline)
        line=line[:-((len(maxlongline)*(1+len(maxlongline))))//2]
    return ''.join(reversed(saves))
def _1_f(line):
        r=re.compile(r'\{(.*?)/.*?\}')
        line=r.sub(lambda x:x.groups()[0],line)
        r=re.compile(r'\{(.*?):.*?\}')
        line=r.sub(lambda x:x.groups()[0],line)
        return line
def _4_f(line):
        line =re.sub('<(.*?)>','',line) 
        line=re.sub('</(.*?)>',"*",line)
        return line
def _6_fEX(line):
        srclang=static_data["language_list_translator_inner"][globalconfig['srclang3']]
        if srclang in ["zh","ja"]:
               white=''
        else:
               white=' '
        line=line.replace('\r',white).replace('\n',white)
        return line
def _6_f(line):
        line=line.replace('\r','').replace('\n','')
        return line
def _91_f(line):
        line=re.sub('([0-9]+)','',line)
        return line
def _92_f(line):
        line=re.sub('([a-zA-Z]+)','',line)
        return line

def _7_zhuanyi_f(line,args): 
        filters=args['替换内容']
        for fil in filters: 
                if fil=="":
                        continue
                else:   
                        line=line.replace(codecs.escape_decode(bytes(fil, "utf-8"))[0].decode("utf-8"),codecs.escape_decode(bytes(filters[fil], "utf-8"))[0].decode("utf-8"))
        return line
def _7_f(line,args): 
        filters=args['替换内容']
        for fil in filters: 
                if fil=="":
                        continue
                else:  
                        line=line.replace( fil ,filters[fil])
        return line
def _8_f(line,args):
        filters=args['替换内容'] 
        for fil in filters: 
                if fil=="":
                        continue
                else:  
                        try:
                                line=re.sub(codecs.escape_decode(bytes(fil, "utf-8"))[0].decode("utf-8"),codecs.escape_decode(bytes(filters[fil], "utf-8"))[0].decode("utf-8"),line)
                        except:
                                print_exc()
        return line

def _remove_non_shiftjis_char(line):
        newline=''
        for char in line:
                try:
                      char.encode('shiftjis')
                      newline+=char
                except:
                      pass
        return newline
def _remove_latin(line):
        newline=''
        for char in line:
                try:
                      char.encode('latin-1')
                except:
                      newline+=char
        return newline
def _remove_ascii(line):
        newline=''
        for char in line:
                try:
                      char.encode('ascii') 
                except:
                      newline+=char
        return newline
def _remove_control(line):
        newline=''
        for r in line:
                _ord=ord(r)
                if _ord<0x20 or (_ord>0x80 and _ord<0xa0):
                    continue
                newline+=r
        return newline
def _remove_not_in_ja_bracket(line): 
        if '「' in line and '」' in line: 
                _1=line.index('「')
                _2=line.rindex('」')
                if _1<_2:
                       return line[_1:_2+1]
        return  line
from myutils.utils import checkchaos
def _remove_chaos(line):
       newline=''
       for c in line:
              if checkchaos(c):
                     continue
              newline+=c
       return newline 


_selfdefpost=None
_selfdefpostmd5=None
def POSTSOLVE(line): 
    global _selfdefpostmd5,_selfdefpost
    if line=="":
        return ""
    functions={
        '_2':_2_f,
        '_3':_3_f,
        '_3_2':_3_2,
        '_10':_10_f,
        '_1':_1_f,
        '_4':_4_f,
        '_6':_6_f,
        '_6EX':_6_fEX,
        '_91':_91_f,
        '_92':_92_f,
        '_7':_7_f,
        '_8':_8_f,
        '_13':_13_f,
        '_13EX':_13_fEX,
        '_7_zhuanyi':_7_zhuanyi_f,
        '_remove_non_shiftjis_char':_remove_non_shiftjis_char,
        "_remove_latin":_remove_latin,
        "_remove_ascii":_remove_ascii,
        "_remove_control":_remove_control,
        "_remove_chaos":_remove_chaos,
        "_remove_not_in_ja_bracket":_remove_not_in_ja_bracket
    }
    useranklist=globalconfig['postprocess_rank']
    usedpostprocessconfig=postprocessconfig
    usemypostpath='./userconfig/mypost.py'
    usemodule='mypost'
    try:
     if 'pname' in dir(gobject.baseobject.textsource):
        exepath=gobject.baseobject.textsource.pname
        if savehook_new_data[exepath]['use_saved_text_process']:
                useranklist=savehook_new_data[exepath]['save_text_process_info']['rank']
                usedpostprocessconfig=savehook_new_data[exepath]['save_text_process_info']['postprocessconfig']
                if savehook_new_data[exepath]['save_text_process_info']['mypost']:
                        usemodule='posts.'+savehook_new_data[exepath]['save_text_process_info']['mypost']
                        usemypostpath='./userconfig/posts/{}.py'.format(savehook_new_data[exepath]['save_text_process_info']['mypost']) 
    except:
       print_exc()     
    try:
           md5=getfilemd5(usemypostpath)
           if md5!=_selfdefpostmd5:
                   _=importlib.import_module(usemodule)
                   _=importlib.reload(_)
                   _selfdefpostmd5=md5
                   _selfdefpost=_
           else:
                  _=_selfdefpost
           functions.update({
                   '_11':_.POSTSOLVE
                  } )
    except ModuleNotFoundError:
           pass
    except:
           print_exc()
           pass

    for postitem in useranklist:
        if postitem not in functions:continue
        if postitem not in usedpostprocessconfig:continue
        if usedpostprocessconfig[postitem]['use']:
                try: 
                        _f=functions[postitem]
                        if _f.__code__.co_argcount==1:
                                line=functions[postitem](line)
                        elif _f.__code__.co_argcount==2:
                                line=functions[postitem](line,usedpostprocessconfig[postitem].get('args',{}))
                        else:
                                raise Exception("unsupported parameters num") 
                        
                except Exception  as e:
                        print_exc()  
                        if postitem=='_11':
                               raise e
    return line