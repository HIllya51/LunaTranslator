import sys
from PyQt5.QtCore import QCoreApplication ,Qt 
from PyQt5.QtWidgets import  QApplication

import os
def initpath(): 
    dirname=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(dirname) 

    if os.path.exists('./userconfig')==False:
        os.mkdir('./userconfig')
    if os.path.exists('./userconfig/memory')==False:
        os.mkdir('./userconfig/memory')
    if os.path.exists('./translation_record')==False:
        os.mkdir('./translation_record') 
    if os.path.exists('./translation_record/cache')==False:
        os.mkdir('./translation_record/cache') 
    if os.path.exists('./cache')==False:
        os.mkdir('./cache')
    if os.path.exists('./cache/ocr')==False:
        os.mkdir('./cache/ocr')
    if os.path.exists('./cache/update')==False:
        os.mkdir('./cache/update')
    if os.path.exists('./cache/screenshot')==False:
        os.mkdir('./cache/screenshot')
    if os.path.exists('./cache/tts')==False:
        os.mkdir('./cache/tts')

    sys.path.append('./userconfig')
   

if __name__ == "__main__" :
    initpath()
    from utils.hwnd import  getScreenRate 
    
    from utils.checkintegrity import checkintegrity
    screenrate=getScreenRate()  

    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) 


    if checkintegrity():
        
        from LunaTranslator import MAINUI
        main = MAINUI(app) 
        main.screen_scale_rate =screenrate
        main.checklang() 
        main.aa() 
        app.exit(app.exec_())
