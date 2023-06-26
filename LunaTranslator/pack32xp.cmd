set targetdir=..\build\LunaTranslator_x86_xp
set targetdir_in=..\build\LunaTranslator_x86_xp\LunaTranslator

rmdir /S /Q %targetdir%

C:\Python34\Scripts\pyinstaller.exe -D -c --specpath %targetdir%\.. --distpath %targetdir% -i C:\dataH\LunaTranslator_x86\LunaTranslator.exe -w LunaTranslator\LunaTranslator_main.py

rename %targetdir%\LunaTranslator_main LunaTranslator

xcopy .\files %targetdir%\files /e /y /I
copy ..\LICENSE %targetdir%\
xcopy .\LunaTranslator\ocrengines %targetdir_in%\ocrengines /e /y /I
xcopy .\LunaTranslator\webresource %targetdir_in%\webresource /e /y /I
xcopy .\LunaTranslator\postprocess %targetdir_in%\postprocess /e /y /I
xcopy .\LunaTranslator\translator %targetdir_in%\translator /e /y /I
xcopy .\LunaTranslator\cishu %targetdir_in%\cishu /e /y /I
xcopy .\LunaTranslator\tts %targetdir_in%\tts /e /y /I
xcopy .\LunaTranslator\hiraparse %targetdir_in%\hiraparse /e /y /I

xcopy C:\Python34\Lib\site-packages\websocket %targetdir_in%\websocket /e /y /I


xcopy ..\plugins\exec\builds\_x86 %targetdir%\ /e /y /I
del %targetdir_in%\Qt5PrintSupport.dll
del %targetdir_in%\Qt5Svg.dll
del %targetdir_in%\PyQt5.QtPrintSupport.pyd

del %targetdir%\files\plugins\ocr64.dll
del %targetdir%\files\plugins\winsharedutils64.dll
del %targetdir%\files\plugins\winrtutils64.dll

del %targetdir%\files\plugins\libmecab64.dll

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


xcopy %targetdir%\ C:\dataH\LunaTranslator_x86_xp /e /y /I