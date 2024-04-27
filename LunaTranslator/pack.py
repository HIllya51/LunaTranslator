import pefile
import os,shutil,sys
print(sys.argv)
x86=int(sys.argv[1])
isdebug=len(sys.argv)>2 and int(sys.argv[2])
if x86:
    nuitkadist=r'..\build\x86\LunaTranslator_main.dist'
    targetdir=r'..\build\LunaTranslator_x86'
    launch=r'..\plugins\builds\_x86'
    downlevel=r'C:\Windows\SysWOW64\downlevel'
    target='LunaTranslator_x86'
    baddll='DLL64'
else:
    baddll='DLL32'
    target='LunaTranslator'
    launch=r'..\plugins\builds\_x64'
    nuitkadist=r'..\build\x64\LunaTranslator_main.dist'
    targetdir=r'..\build\LunaTranslator'
    downlevel=r'C:\Windows\system32\downlevel'
if isdebug:
    targetdir+=r'_debug'
    target+='_debug'
    if x86:
        nuitkadist=r'..\build\x86_debug\LunaTranslator_main.dist'
    else:
        nuitkadist=r'..\build\x64_debug\LunaTranslator_main.dist'


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

for f in ['transoptimi','hiraparse','ocrengines','translator','cishu','tts','network','textoutput','scalemethod']:
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

shutil.copy(rf'{downlevel}\ucrtbase.dll',targetdir_in)
collect=[]
for _dir,_,fs in os.walk(targetdir):
    for f in fs:
        collect.append(os.path.join(_dir,f))
for f in collect:
    if f.endswith('.pyc') or f.endswith('Thumbs.db'):
        os.remove(f)
    elif f.endswith('.exe') or f.endswith('.pyd') or f.endswith('.dll'):
        
        try:
            pe = pefile.PE(f)
            import_table = pe.DIRECTORY_ENTRY_IMPORT
            imports=[]
            for entry in import_table:
                if entry.dll.decode("utf-8").lower().startswith('api'):
                    imports.append(entry.dll.decode("utf-8"))
            pe.close()
        except:
            continue
        if f.endswith('Magpie.Core.exe'):continue
        if f.endswith('QtWidgets.pyd'):
            imports+=['api-ms-win-crt-runtime-l1-1-0.dll','api-ms-win-crt-heap-l1-1-0.dll'] 
            #pefile好像有bug，仅对于QtWidgets.pyd这个文件，只能读取到导入了Qt5Widgets.dll
        print(f,imports)
        if len(imports)==0:continue
        with open(f,'rb') as ff:
            bs=bytearray(ff.read())
        for _dll in imports:
            if _dll.lower().startswith('api-ms-win-core'):
                #其实对于api-ms-win-core-winrt-XXX实际上是到ComBase.dll之类的，不过此项目中不包含这些
                _target='kernel32.dll'
            elif _dll.lower().startswith('api-ms-win-crt'):
                _target='ucrtbase.dll'
            _dll=_dll.encode()
            _target=_target.encode()
            idx=bs.find(_dll)
            #print(len(bs))
            bs[idx:idx+len(_dll)]=_target+b'\0'*(len(_dll)-len(_target))
            #print(len(bs))
        with open(f,'wb') as ff:
            ff.write(bs)

if os.path.exists(rf'{targetdir}\..\{target}.zip'):
    os.remove(rf'{targetdir}\..\{target}.zip')
if os.path.exists(rf'{targetdir}\..\{target}.7z'):
    os.remove(rf'{targetdir}\..\{target}.7z')
os.system(rf'"C:\Program Files\7-Zip\7z.exe" a -m0=Deflate -mx9 {targetdir}\..\{target}.zip {targetdir}')
os.system(rf'"C:\Program Files\7-Zip\7z.exe" a -m0=LZMA2 -mx9 {targetdir}\..\{target}.7z {targetdir}')

with open(r'C:\Program Files\7-Zip\7z.sfx','rb') as ff:
    sfx=ff.read()

config='''
;!@Install@!UTF-8!


;!@InstallEnd@!
'''
with open(rf'{targetdir}\..\{target}.7z','rb') as ff:
    data=ff.read()

with open(rf'{targetdir}\..\{target}.exe','wb') as ff:
    ff.write(sfx)
    ff.write(config.encode('utf8'))
    ff.write(data)