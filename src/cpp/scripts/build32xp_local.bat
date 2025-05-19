set https_proxy=http://127.0.0.1:7897
call dobuildxp.bat
copy ..\builds\_x86_xp\shareddllproxy32.exe ..\..\files
robocopy ..\builds\_x86_xp ..\..\files\DLL32 *.dll