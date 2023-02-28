rmdir /S /Q ..\build\x86\Lunatranslator 
xcopy ..\build\x86\LunaTranslator_main.dist ..\build\LunaTranslator_x86\LunaTranslator /e /y /I
xcopy .\files ..\build\LunaTranslator_x86\files /e /y /I
copy ..\LICENSE ..\build\LunaTranslator_x86\
xcopy .\LunaTranslator\ocrengines ..\build\LunaTranslator_x86\LunaTranslator\ocrengines /e /y /I
xcopy .\LunaTranslator\postprocess ..\build\LunaTranslator_x86\LunaTranslator\postprocess /e /y /I
xcopy .\LunaTranslator\translator ..\build\LunaTranslator_x86\LunaTranslator\translator /e /y /I
xcopy .\LunaTranslator\cishu ..\build\LunaTranslator_x86\LunaTranslator\cishu /e /y /I
xcopy ..\dependence\dependence32 ..\build\LunaTranslator_x86\LunaTranslator /e /y /I 
xcopy ..\dependence\api-ms-win_32 ..\build\LunaTranslator_x86\LunaTranslator /e /y /I
xcopy ..\dependence\exe32 ..\build\LunaTranslator_x86\ /e /y /I
del ..\build\LunaTranslator_x86\LunaTranslator\qt5qml.dll
del ..\build\LunaTranslator_x86\LunaTranslator\qt5qmlmodels.dll
del ..\build\LunaTranslator_x86\LunaTranslator\qt5quick.dll
del ..\build\LunaTranslator_x86\LunaTranslator\qt5printsupport.dll
del ..\build\LunaTranslator_x86\LunaTranslator\qt5websockets.dll
del ..\build\LunaTranslator_x86\LunaTranslator\qt5dbus.dll
del ..\build\LunaTranslator_x86\LunaTranslator\qt5multimedia.dll
del ..\build\LunaTranslator_x86\LunaTranslator\PyQt5\qt-plugins\platforms\qminimal.dll
del ..\build\LunaTranslator_x86\LunaTranslator\PyQt5\qt-plugins\platforms\qoffscreen.dll
del ..\build\LunaTranslator_x86\LunaTranslator\PyQt5\qt-plugins\platforms\qwebgl.dll
rmdir /S /Q ..\build\LunaTranslator_x86\LunaTranslator\PyQt5\qt-plugins\mediaservice
rmdir /S /Q ..\build\LunaTranslator_x86\LunaTranslator\PyQt5\qt-plugins\printsupport
rmdir /S /Q ..\build\LunaTranslator_x86\LunaTranslator\PyQt5\qt-plugins\imageformats 
del ..\build\LunaTranslator_x86\LunaTranslator\libssl-1_1-x64.dll
del ..\build\LunaTranslator_x86\LunaTranslator\libcrypto-1_1-x64.dll

del ..\build\LunaTranslator_x86\files\ocr.dll
del ..\build\LunaTranslator_x86\files\embedded5\Qt5Network.dll
del ..\build\LunaTranslator_x86\files\embedded5\Qt5Core.dll
copy ..\dependence\ocr32 ..\build\LunaTranslator_x86\files

xcopy ..\build\LunaTranslator_x86\ C:\dataH\LunaTranslator /e /y /I
pause