import shutil,sys
x86=int(sys.argv[1])
if x86:
    shutil.copy('../builds/_x86/shareddllproxy32.exe','../../py/files/plugins')
    shutil.copy('../builds/_x86/winrtutils32.dll','../../py/files/plugins/DLL32')
    shutil.copy('../builds/_x86/winsharedutils32.dll','../../py/files/plugins/DLL32')
    shutil.copy('../builds/_x86/wcocr.dll','../../py/files/plugins/DLL32')
    shutil.copy('../builds/_x86/LunaOCR32.dll','../../py/files/plugins/DLL32')
else:
    shutil.copy('../builds/_x64/shareddllproxy64.exe','../../py/files/plugins')
    shutil.copy('../builds/_x64/hookmagpie.dll','../../py/files/plugins')
    shutil.copy('../builds/_x64/winrtutils64.dll','../../py/files/plugins/DLL64')
    shutil.copy('../builds/_x64/winsharedutils64.dll','../../py/files/plugins/DLL64')
    shutil.copy('../builds/_x64/wcocr.dll','../../py/files/plugins/DLL64')
    shutil.copy('../builds/_x64/LunaOCR64.dll','../../py/files/plugins/DLL64')
