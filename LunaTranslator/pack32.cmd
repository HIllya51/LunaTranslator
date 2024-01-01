set targetdir=..\build\LunaTranslator_x86
set targetdir_in=..\build\LunaTranslator_x86\LunaTranslator
set pythonlib=%LOCALAPPDATA%\Programs\Python\Python37-32\Lib
set pythondll=%LOCALAPPDATA%\Programs\Python\Python37-32\DLLs
set pythonpackage=%pythonlib%\site-packages

rmdir /S /Q %targetdir%
xcopy ..\build\x86\LunaTranslator_main.dist %targetdir_in% /e /y /I
xcopy .\files %targetdir%\files /e /y /I
copy ..\LICENSE %targetdir%\
xcopy .\LunaTranslator\ocrengines %targetdir_in%\ocrengines /e /y /I
xcopy .\LunaTranslator\webresource %targetdir_in%\webresource /e /y /I
xcopy .\LunaTranslator\postprocess %targetdir_in%\postprocess /e /y /I
xcopy .\LunaTranslator\translator %targetdir_in%\translator /e /y /I
xcopy .\LunaTranslator\cishu %targetdir_in%\cishu /e /y /I
xcopy .\LunaTranslator\tts %targetdir_in%\tts /e /y /I
xcopy .\LunaTranslator\hiraparse %targetdir_in%\hiraparse /e /y /I
xcopy .\LunaTranslator\network %targetdir_in%\network /e /y /I

xcopy ..\plugins\exec\builds\_x86 %targetdir%\ /e /y /I
del %targetdir_in%\qt5qml.dll
del %targetdir_in%\qt5qmlmodels.dll
del %targetdir_in%\qt5quick.dll
del %targetdir_in%\qt5printsupport.dll
del %targetdir_in%\qt5websockets.dll
del %targetdir_in%\qt5dbus.dll
del %targetdir_in%\qt5multimedia.dll
del %targetdir_in%\qt5svg.dll
del %targetdir_in%\qt5network.dll

del %targetdir_in%\PyQt5\qt-plugins\platforms\qminimal.dll
del %targetdir_in%\PyQt5\qt-plugins\platforms\qwebgl.dll
rmdir /S /Q %targetdir_in%\PyQt5\qt-plugins\mediaservice
rmdir /S /Q %targetdir_in%\PyQt5\qt-plugins\printsupport
rmdir /S /Q %targetdir_in%\PyQt5\qt-plugins\platformthemes
rmdir /S /Q %targetdir_in%\PyQt5\qt-plugins\iconengines

del %targetdir_in%\concrt140.dll
del %targetdir_in%\libssl-1_1.dll
del %targetdir_in%\libcrypto-1_1.dll
del %targetdir_in%\libeay32.dll
del %targetdir_in%\ssleay32.dll
del %targetdir_in%\_ssl.pyd
 


del %targetdir%\files\plugins\libcurl-x64.dll
del %targetdir%\files\plugins\ocr64.dll
del %targetdir%\files\plugins\winsharedutils64.dll
del %targetdir%\files\plugins\winrtutils64.dll
del %targetdir%\files\plugins\libmecab64.dll


xcopy ..\binary\api-ms-win_32 %targetdir_in% /e /y /I

@echo off
setlocal enabledelayedexpansion

set "directory=%targetdir%"

if "%directory%" == "" (
    set /p directory="Enter directory path: "
)

for /f "delims=" %%i in ('dir /b /s "%directory%\*.pyc"') do (
    del "%%i"
)

for /f "delims=" %%d in ('dir /s /b /a:d "%directory%" ^| sort /r') do (
    rd "%%d" 2>nul
)

del %targetdir%\..\LunaTranslator_x86.zip
"C:\Program Files\7-Zip\7z.exe" a -m0=LZMA -mx9 %targetdir%\..\LunaTranslator_x86.zip %targetdir%

xcopy %targetdir%\ C:\dataH\LunaTranslator_x86 /e /y /I