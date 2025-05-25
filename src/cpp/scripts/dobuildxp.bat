@echo off
setlocal enabledelayedexpansion
goto :main

:get_host_arch
    setlocal
    set out_var=%~1
    if defined PROCESSOR_ARCHITEW6432 (
        set "host_arch=%PROCESSOR_ARCHITEW6432%"
    ) else (
        set "host_arch=%PROCESSOR_ARCHITECTURE%"
    )
    if "%host_arch%" == "AMD64" (
        set result=x64
    ) else if "%host_arch%" == "x86" (
        set result=x86
    ) else (
        echo ERROR: Unsupported host machine architecture.
        endlocal
        exit /b 1
    )
    endlocal & set %out_var%=%result%
    goto :eof

:find_msvc
    setlocal
    set out_var=%~1
    rem Find vswhere.exe
    set "vswhere=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
    if not exist "%vswhere%" set "vswhere=!ProgramFiles!\Microsoft Visual Studio\Installer\vswhere.exe"
    if not exist "%vswhere%" (
        echo ERROR: Failed to find vswhere.exe>&2
        endlocal & exit /b 1
    )
    rem Find VC tools
    for /f "usebackq tokens=*" %%i in (`"%vswhere%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do (
        set vc_dir=%%i
    )
    if not exist "%vc_dir%\Common7\Tools\vsdevcmd.bat" (
        echo ERROR: Failed to find MSVC.>&2
        endlocal & exit /b 1
    )
    endlocal & set "%out_var%=%vc_dir%"
    goto :eof

:activate_msvc
    where cl.exe > nul 2>&1 && goto :eof || cmd /c exit 0
    call :find_msvc vc_dir || goto :eof
    call "%vc_dir%\Common7\Tools\vsdevcmd.bat" -no_logo -arch=%~1 || goto :eof
    goto :eof


:main
    call :get_host_arch host_arch || exit /b
    if not defined TARGET_ARCH (
        rem Target architecture is by default the same as the host architecture
        set target_arch=%host_arch%
    )
    call :activate_msvc "%target_arch%" || goto :eof
    msbuild ..\build\x86_winxp\LunaPlugins.sln -p:Configuration=Release
    goto :eof
