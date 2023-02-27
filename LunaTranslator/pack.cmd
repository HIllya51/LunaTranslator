rmdir /S /Q ..\build\Lunatranslator 
xcopy ..\build\LunaTranslator_main.dist ..\build\LunaTranslator\LunaTranslator /e /y /I
xcopy .\files ..\build\LunaTranslator\files /e /y /I
copy ..\LICENSE ..\build\LunaTranslator\
xcopy ..\CXXplugins\EXE ..\build\LunaTranslator\ /e /y /I
xcopy .\LunaTranslator\ocrengines ..\build\LunaTranslator\LunaTranslator\ocrengines /e /y /I
xcopy .\LunaTranslator\postprocess ..\build\LunaTranslator\LunaTranslator\postprocess /e /y /I
xcopy .\LunaTranslator\translator ..\build\LunaTranslator\LunaTranslator\translator /e /y /I
xcopy .\LunaTranslator\cishu ..\build\LunaTranslator\LunaTranslator\cishu /e /y /I
xcopy ..\dependence ..\build\LunaTranslator\LunaTranslator /e /y /I
del ..\build\LunaTranslator\LunaTranslator\qt5qml.dll
del ..\build\LunaTranslator\LunaTranslator\qt5qmlmodels.dll
del ..\build\LunaTranslator\LunaTranslator\qt5quick.dll
del ..\build\LunaTranslator\LunaTranslator\qt5printsupport.dll
del ..\build\LunaTranslator\LunaTranslator\qt5websockets.dll
del ..\build\LunaTranslator\LunaTranslator\qt5dbus.dll
del ..\build\LunaTranslator\LunaTranslator\qt5multimedia.dll
del ..\build\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\platforms\qminimal.dll
del ..\build\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\platforms\qoffscreen.dll
del ..\build\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\platforms\qwebgl.dll
rmdir /S /Q ..\build\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\mediaservice
rmdir /S /Q ..\build\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\printsupport
rmdir /S /Q ..\build\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\imageformats

xcopy ..\build\LunaTranslator\ C:\dataH\LunaTranslator /e /y /I
pause