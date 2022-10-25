# wincom.pri
# 8/11/2014 jichi
win32 {

DEFINES += WITH_LIB_WINCOM

INCLUDEPATH += $$SAPI_HOME/include
#LIBS  += -lole32

DEPENDPATH += $$PWD

HEADERS += \
  $$PWD/wincom.h \
  $$PWD/wincomptr.h

#SOURCES += $$PWD/wintts.cc
}

# EOF
