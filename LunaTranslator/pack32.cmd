rmdir /S /Q ..\build\x86\Lunatranslator 
xcopy ..\build\x86\LunaTranslator_main.dist ..\build\x86\LunaTranslator\LunaTranslator /e /y /I
xcopy .\files ..\build\x86\LunaTranslator\files /e /y /I
copy ..\LICENSE ..\build\x86\LunaTranslator\
xcopy .\LunaTranslator\ocrengines ..\build\x86\LunaTranslator\LunaTranslator\ocrengines /e /y /I
xcopy .\LunaTranslator\postprocess ..\build\x86\LunaTranslator\LunaTranslator\postprocess /e /y /I
xcopy .\LunaTranslator\translator ..\build\x86\LunaTranslator\LunaTranslator\translator /e /y /I
xcopy .\LunaTranslator\cishu ..\build\x86\LunaTranslator\LunaTranslator\cishu /e /y /I
xcopy ..\dependence\dependence32 ..\build\x86\LunaTranslator\LunaTranslator /e /y /I 
xcopy ..\dependence\api-ms-win_32 ..\build\x86\LunaTranslator\LunaTranslator /e /y /I
xcopy ..\dependence\exe32 ..\build\x86\LunaTranslator\ /e /y /I
del ..\build\x86\LunaTranslator\LunaTranslator\qt5qml.dll
del ..\build\x86\LunaTranslator\LunaTranslator\qt5qmlmodels.dll
del ..\build\x86\LunaTranslator\LunaTranslator\qt5quick.dll
del ..\build\x86\LunaTranslator\LunaTranslator\qt5printsupport.dll
del ..\build\x86\LunaTranslator\LunaTranslator\qt5websockets.dll
del ..\build\x86\LunaTranslator\LunaTranslator\qt5dbus.dll
del ..\build\x86\LunaTranslator\LunaTranslator\qt5multimedia.dll
del ..\build\x86\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\platforms\qminimal.dll
del ..\build\x86\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\platforms\qoffscreen.dll
del ..\build\x86\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\platforms\qwebgl.dll
rmdir /S /Q ..\build\x86\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\mediaservice
rmdir /S /Q ..\build\x86\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\printsupport
rmdir /S /Q ..\build\x86\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\imageformats 
del ..\build\x86\LunaTranslator\LunaTranslator\libssl-1_1-x64.dll
del ..\build\x86\LunaTranslator\LunaTranslator\libcrypto-1_1-x64.dll

del ..\build\x86\LunaTranslator\files\ocr.dll
copy ..\dependence\ocr32 ..\build\x86\LunaTranslator\files

xcopy ..\build\x86\LunaTranslator\ C:\dataH\LunaTranslator /e /y /I
pause