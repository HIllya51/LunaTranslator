from textsource.copyboard import copyboard
from textsource.namepipe import namepipe
from textsource.ocrtext import ocrtext

from translators.goog import GOO 
from translators.baidu import BD 
from translators.bing import BINGFY

from translators.ali import ALI

import threading, time, signal
from translators.youdao import youdaots
import sys
from hira import hira
def quit(signum, frame): 
    sys.exit()
if __name__=='__main__':
    
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    print('initializing')
    goo=GOO()
    bing=BINGFY()
    bd=BD()
    ali=ALI()
    youdao=youdaots()
    print('OK') 

    hira_=hira()
    def textgetmethod(paste_str):
        hira_.fy(paste_str)  
            
        goo.gettask(paste_str)
        bd.gettask(paste_str)
        bing.gettask(paste_str)
        ali.gettask(paste_str)
        youdao.gettask(paste_str)
    copy=ocrtext(textgetmethod)
    while True:
        time.sleep(999)