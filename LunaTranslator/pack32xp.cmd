set targetdir=..\build\LunaTranslator_x86_xp

rmdir /S /Q %targetdir%\LunaTranslator
rmdir /S /Q %targetdir%\files
rmdir /S /Q %targetdir%\cache
rmdir /S /Q %targetdir%\userconfig
rmdir /S /Q %targetdir%\translation_record

xcopy .\LunaTranslator %targetdir%\LunaTranslator /e /y /I
xcopy .\files %targetdir%\files /e /y /I
copy ..\binary\LunaTranslator_xp.exe %targetdir% 


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
