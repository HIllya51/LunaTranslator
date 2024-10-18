import shutil,sys
x86=int(sys.argv[1])
if x86:
    shutil.copy('../builds/_x86/shareddllproxy32.exe','../../LunaTranslator/files/plugins')
    shutil.copy('../builds/_x86/loopbackaudio.dll','../../LunaTranslator/files/plugins/DLL32')
    shutil.copy('../builds/_x86/winrtutils32.dll','../../LunaTranslator/files/plugins/DLL32')
    shutil.copy('../builds/_x86/winsharedutils32.dll','../../LunaTranslator/files/plugins/DLL32')
    shutil.copy('../builds/_x86/wcocr.dll','../../LunaTranslator/files/plugins/DLL32')
else:
    shutil.copy('../builds/_x64/shareddllproxy64.exe','../../LunaTranslator/files/plugins')
    shutil.copy('../builds/_x64/loopbackaudio.dll','../../LunaTranslator/files/plugins/DLL64')
    shutil.copy('../builds/_x64/hookmagpie.dll','../../LunaTranslator/files/plugins')
    shutil.copy('../builds/_x64/winrtutils64.dll','../../LunaTranslator/files/plugins/DLL64')
    shutil.copy('../builds/_x64/winsharedutils64.dll','../../LunaTranslator/files/plugins/DLL64')
    shutil.copy('../builds/_x64/wcocr.dll','../../LunaTranslator/files/plugins/DLL64')
