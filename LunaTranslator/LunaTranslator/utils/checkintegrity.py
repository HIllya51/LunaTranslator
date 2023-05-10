import platform,os
from utils.config import _TR
import win32utils
def checkintegrity():
    flist=[
         './files/plugins/shareddllproxy32.exe',
         './files/plugins/shareddllproxy64.exe',
         './files/plugins/LunaHook/LunaHook32.dll',
         './files/plugins/LunaHook/LunaHook64.dll',
         './files/plugins/LunaEmbedder/vnragent.dll',
         './files/plugins/WinOCR.exe',
         './files/plugins/LoaderDll.dll',
         './files/plugins/LocaleEmulator.dll',
    ]
    print(platform.architecture())
    if platform.architecture()[0]=='64bit':
        flist+=[ 
            './files/plugins/winsharedutils64.dll',
            './files/plugins/ocr64.dll', 
        ]
    else:
        flist+=[ 
            './files/plugins/winsharedutils32.dll',
            './files/plugins/ocr32.dll', 
        ]
    collect=[]
    print(flist)
    for f in flist:
        if os.path.exists(f)==False:
            collect.append(f)
    if len(collect):
        win32utils.MessageBox(None,_TR("找不到重要组件：")+'\n'+'\n'.join(collect)+'\n'+_TR('请重新下载并关闭杀毒软件后重试'),_TR("错误"),0)
        return False
    else:
        return True