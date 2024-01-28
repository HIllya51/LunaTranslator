import pefile
import os,shutil,sys
print(sys.argv)
x86=int(sys.argv[1])
if x86:
    nuitkadist=r'..\build\x86\LunaTranslator_main.dist'
    targetdir=r'..\build\LunaTranslator_x86'
    launch=r'..\plugins\builds\_x86'
    downlevel=f'C:\Windows\SysWOW64\downlevel'
    target='LunaTranslator_x86.zip'
    baddll='DLL64'
else:
    baddll='DLL32'
    target='LunaTranslator.zip'
    launch=r'..\plugins\builds\_x64'
    nuitkadist=r'..\build\x64\LunaTranslator_main.dist'
    targetdir=r'..\build\LunaTranslator'
    downlevel=f'C:\Windows\system32\downlevel'
targetdir_in=rf'{targetdir}\LunaTranslator'
def get_import_table(file_path):
    pe = pefile.PE(file_path) 
    import_dlls=[] 
    if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            dll_name = entry.dll.decode("utf-8")  
            import_dlls.append(dll_name) 
    return import_dlls 
 

if os.path.exists(targetdir):
    shutil.rmtree(targetdir)
shutil.copytree(nuitkadist,targetdir_in)
for f in ['LunaTranslator_admin.exe','LunaTranslator.exe']:
    shutil.copy(os.path.join(launch,f),targetdir)
shutil.copytree(r'.\files',rf'{targetdir}\files')
shutil.copy(r'..\LICENSE',targetdir) 

for f in ['hiraparse','ocrengines','translator','cishu','tts','network']:
    shutil.copytree(rf'.\LunaTranslator\{f}',rf'{targetdir_in}\{f}') 

def remove(f):
    if os.path.isdir(f): shutil.rmtree(f)
    else:  os.remove(f)
 
for f in [
    'concrt140.dll','libssl-1_1.dll','libcrypto-1_1.dll','libeay32.dll','ssleay32.dll','_ssl.pyd',
    'qt5qml.dll','qt5qmlmodels.dll','qt5quick.dll','qt5printsupport.dll','qt5websockets.dll','qt5dbus.dll','qt5multimedia.dll','qt5svg.dll','qt5network.dll',
    r'PyQt5\qt-plugins\mediaservice',r'PyQt5\qt-plugins\printsupport',r'PyQt5\qt-plugins\platformthemes',r'PyQt5\qt-plugins\iconengines',r'PyQt5\qt-plugins\platforms\qminimal.dll',r'PyQt5\qt-plugins\platforms\qwebgl.dll'
    ]:
    remove(rf'{targetdir_in}\{f}') 
for f in ['imageformats','platforms','styles']:
    os.rename(rf'{targetdir_in}\PyQt5\qt-plugins\{f}',rf'{targetdir_in}\{f}')

remove(rf'{targetdir}\files\plugins\{baddll}')

collect=[]
for _dir,_,fs in os.walk(targetdir):
    for f in fs:
        collect.append(os.path.join(_dir,f))
dlls=[]
for f in collect:
    if f.endswith('.pyc') or f.endswith('Thumbs.db'):
        os.remove(f)
    elif f.endswith('.exe') or f.endswith('.pyd') or f.endswith('.dll'):
        print(f)
        dlls+=get_import_table(f) 
dlls+=get_import_table(rf'{downlevel}\ucrtbase.dll')+['ucrtbase.dll']
for f in set(dlls):
    if os.path.exists(rf'{targetdir_in}\{f}'):
        continue
    elif os.path.exists(rf'{downlevel}\{f}'):
        shutil.copy(rf'{downlevel}\{f}',targetdir_in)
if os.path.exists(rf'{targetdir}\..\{target}'):
    os.remove(rf'{targetdir}\..\{target}')
os.system(rf'"C:\Program Files\7-Zip\7z.exe" a -m0=LZMA -mx9 {targetdir}\..\{target} {targetdir}')