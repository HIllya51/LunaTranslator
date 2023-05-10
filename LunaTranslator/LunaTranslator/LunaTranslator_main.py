import sys
from PyQt5.QtCore import QCoreApplication ,Qt 
from PyQt5.QtWidgets import  QApplication

from utils.hwnd import  getScreenRate 
from utils.somedef import initpath
from utils.checkintegrity import checkintegrity
if __name__ == "__main__" :
    initpath() 
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
