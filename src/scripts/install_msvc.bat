@REM https://github.com/zufuliu/notepad4/blob/160a40bc20682c42bc866b4f60e2460217a43db4/build/install_msvc.bat
@ECHO OFF
@rem used for GitHub Actions
SetLocal EnableExtensions

SET "Win10Lib=C:\Program Files (x86)\Windows Kits\10\Lib"
SET "VSINSTALLER=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vs_installer.exe"
SET "VSPATH=C:\Program Files\Microsoft Visual Studio\2022\Enterprise"

IF /I "%~1" == "arm" (
	SHIFT
	robocopy "%Win10Lib%\10.0.22621.0\ucrt\arm" "%Win10Lib%\10.0.26100.0\ucrt\arm" /E 1>NUL
	robocopy "%Win10Lib%\10.0.22621.0\um\arm" "%Win10Lib%\10.0.26100.0\um\arm" /E 1>NUL
)

IF /I "%~1" == "v141_xp" (
	SHIFT
	"%VSINSTALLER%" modify --installPath "%VSPATH%" --add Microsoft.VisualStudio.Component.WinXP --norestart --nocache
)