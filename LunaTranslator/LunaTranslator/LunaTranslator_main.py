import sys
from PyQt5.QtCore import Qt 
from PyQt5.QtWidgets import  QApplication
from PyQt5.QtGui import QFont
import platform,os

if __name__ == "__main__" :
    # dirname=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # os.chdir(dirname) 

    if os.path.exists('./userconfig')==False:
        os.mkdir('./userconfig')
    if os.path.exists('./userconfig/memory')==False:
        os.mkdir('./userconfig/memory')
    if os.path.exists('./userconfig/posts')==False:
        os.mkdir('./userconfig/posts')
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
    if os.path.exists('./cache/icon')==False:
        os.mkdir('./cache/icon')
        
    from myutils.config import _TR,static_data,testpriv,globalconfig

    sys.path.append('./userconfig')
    sys.path.insert(0,'./LunaTranslator/network/'+['winhttp','libcurl'][globalconfig['network']])
 
    
    from gui.usefulwidget import getQMessageBox
    from LunaTranslator import MAINUI
    import gobject 

    gobject.overridepathexists()
    
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    font=QFont()
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    QApplication.setFont(font)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) 

    js=static_data['checkintegrity']
    flist=js['shared']
    if platform.architecture()[0]=="64bit":
        flist+=js['64']
    else:
        flist+=js['32']
    collect=[] 
    for f in flist:
        if os.path.exists(f)==False:
            collect.append(f)
    if len(collect):
        getQMessageBox(None,_TR("错误"),_TR("找不到重要组件：")+"\n"+"\n".join(collect)+"\n"+_TR("请重新下载并关闭杀毒软件后重试"),tr=False)
        os._exit(0) 
    
    try:
        testpriv()
    except:
        getQMessageBox(None,"错误","当前路径读写权限不足，请使用管理员权限运行！")
        os._exit(0) 
    
    gobject.baseobject=MAINUI(app) 
    gobject.baseobject.checklang() 
    gobject.baseobject.aa() 
    app.exit(app.exec_())
