set https_proxy=http://127.0.0.1:7897
call dobuildxp.bat
copy ..\builds\_x86\shareddllproxy32.exe ..\..\files\plugins
robocopy ..\builds\_x86 ..\..\files\plugins\DLL32 *.dll