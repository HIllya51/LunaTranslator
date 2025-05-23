set https_proxy=http://127.0.0.1:7897
call dobuildxp.bat
copy ..\builds\_x86_winxp\shareddllproxy32.exe ..\..\files
robocopy ..\builds\_x86_winxp ..\..\files\DLL32 *.dll