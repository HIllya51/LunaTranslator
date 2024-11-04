import shutil,sys
x86=int(sys.argv[1])
if x86:
    shutil.copy('../builds/_x86/shareddllproxy32.exe','../../files/plugins')
    shutil.copy('../builds/_x86/loopbackaudio.dll','../../files/plugins/DLL32')
    shutil.copy('../builds/_x86/winrtutils32.dll','../../files/plugins/DLL32')
    shutil.copy('../builds/_x86/winsharedutils32.dll','../../files/plugins/DLL32')
    shutil.copy('../builds/_x86/wcocr.dll','../../files/plugins/DLL32')
    shutil.copy('../builds/_x86/LunaOCR32.dll','../../files/plugins/DLL32')
else:
    shutil.copy('../builds/_x64/shareddllproxy64.exe','../../files/plugins')
    shutil.copy('../builds/_x64/loopbackaudio.dll','../../files/plugins/DLL64')
    shutil.copy('../builds/_x64/hookmagpie.dll','../../files/plugins')
    shutil.copy('../builds/_x64/winrtutils64.dll','../../files/plugins/DLL64')
    shutil.copy('../builds/_x64/winsharedutils64.dll','../../files/plugins/DLL64')
    shutil.copy('../builds/_x64/wcocr.dll','../../files/plugins/DLL64')
    shutil.copy('../builds/_x64/LunaOCR64.dll','../../files/plugins/DLL64')
