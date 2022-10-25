#ifndef MONOOBJECT_H
#define MONOOBJECT_H

// monoobject.h
// 12/26/2014 jichi
// https://github.com/mono/mono/blob/master/mono/metadata/object.h
// https://github.com/mono/mono/blob/master/mono/metadata/object-internals.h
// https://github.com/mono/mono/blob/master/mono/util/mono-publib.h

#include <cstdint>

#define MONO_ZERO_LEN_ARRAY 1

// mono/io-layer/uglify.h
//typedef int8_t gint8;
//typedef int32_t gint32;
//typedef wchar_t gunichar2; // either char or wchar_t, depending on how mono is compiled

typedef int32_t		mono_bool;
typedef uint8_t		mono_byte;
typedef uint16_t	mono_unichar2;
typedef uint32_t	mono_unichar4;

// mono/metadata/object.h

typedef mono_bool MonoBoolean;

struct MonoArray;
struct MonoDelegate;
struct MonoDomain;
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
  int32_t length;
  mono_unichar2 chars[MONO_ZERO_LEN_ARRAY];
};

#endif // MONOOBJECT_H
