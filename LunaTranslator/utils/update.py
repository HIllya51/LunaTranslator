
import win32api,os,win32con
def update():
    with open('./cache/update/update.bat','w',encoding='utf8') as ff:
                
                ff.write(r'''

:rekill1
taskkill /F /IM LunaTranslator_main.exe
tasklist | find /i "LunaTranslator_main.exe" && go rekill || echo "fuck"
:rekill2
taskkill /F /IM LunaTranslator.exe
tasklist | find /i "LunaTranslator.exe" && go rekill || echo "fuck"
:rekill
taskkill /F /IM LunaTranslator_no_Admin.exe  
tasklist | find /i "LunaTranslator_no_Admin.exe" && go rekill || echo "fuck"

:trydel1
del LunaTranslator\LunaTranslator_main.exe
if exist LunaTranslator\LunaTranslator_main.exe goto trydel1
:trydel2
del LunaTranslator_no_Admin.exe
if exist LunaTranslator_no_Admin.exe goto trydel2
:trydel3
del LunaTranslator.exe
if exist LunaTranslator.exe goto trydel3

xcopy .\cache\update\LunaTranslator\ .\ /s /e /c /y /h /r 
exit
                
                ''') 
            #subprocess.Popen('cache\\update\\update.bat' ,shell=True)
    win32api.ShellExecute(None, "open", 'cache\\update\\update.bat', "", os.path.dirname('.'), win32con.SW_HIDE)