#pragma once

// mono/types.h
// 12/26/2014
// https://github.com/mono/mono/blob/master/mono/metadata/object.h
// http://api.xamarin.com/index.aspx?link=xhtml%3Adeploy%2Fmono-api-string.html

#include <cstdint>

// mono/io-layer/uglify.h
typedef int8_t gint8;
typedef int32_t gint32;
typedef wchar_t gunichar2; // either char or wchar_t, depending on how mono is compiled

typedef gint8 mono_byte;
typedef gunichar2 mono_unichar2;

// mono/metadata/object.h

typedef mono_byte MonoBoolean;

struct MonoArray;
struct MonoDelegate;
struct MonoException;
struct MonoString;
struct MonoThreadsSync;
struct MonoThread;
struct MonoVTable;

struct MonoObject {
  MonoVTable *vtable;
  MonoThreadsSync *synchronisation;
};

struct MonoString {
  MonoObject object;
  gint32 length;
  gunichar2 chars[0];
};

// EOF
