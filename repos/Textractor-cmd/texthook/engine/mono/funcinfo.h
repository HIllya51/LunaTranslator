#pragma once

// mono/funcinfo.h
// 12/26/2014
// https://github.com/mono/mono/blob/master/mono/metadata/object.h
// http://api.xamarin.com/index.aspx?link=xhtml%3Adeploy%2Fmono-api-string.html
// http://docs.go-mono.com/index.aspx?link=xhtml%3Adeploy%2Fmono-api-string.html

//#include "ith/import/mono/types.h"

// MonoString*    mono_string_new            (MonoDomain *domain,
//                                            const char *text);
// MonoString*    mono_string_new_len        (MonoDomain *domain,
//                                            const char *text,
//                                            guint length);
// MonoString*    mono_string_new_size       (MonoDomain *domain,
//                                            gint32 len);
// MonoString*    mono_string_new_utf16      (MonoDomain *domain,
//                                            const guint16 *text,
//                                            gint32 len);
// MonoString*    mono_string_from_utf16     (gunichar2 *data);
// mono_unichar2* mono_string_to_utf16       (MonoString *s);
// char*          mono_string_to_utf8        (MonoString *s);
// gboolean       mono_string_equal          (MonoString *s1,
//                                            MonoString *s2);
// guint          mono_string_hash           (MonoString *s);
// MonoString*    mono_string_intern         (MonoString *str);
// MonoString*    mono_string_is_interned    (MonoString *o);
// MonoString*    mono_string_new_wrapper    (const char *text);
// gunichar2*     mono_string_chars          (MonoString *s);
// int            mono_string_length         (MonoString *s);
// gunichar2*     mono_unicode_from_external (const gchar *in, gsize *bytes);
// gchar*         mono_unicode_to_external   (const gunichar2 *uni);
// gchar*         mono_utf8_from_external    (const gchar *in);

struct MonoFunction { // argument indices start from 0 for SpecialHookMonoString, otherwise 1
  const char *functionName;
  size_t textIndex; // argument index
  short lengthIndex; // argument index
  unsigned long hookType; // HookParam type
  void(*text_fun)(DWORD stack, HookParam* hp, BYTE obsoleteAlwaysZero, DWORD* data, DWORD* split, DWORD* len); // HookParam::text_fun_t
};

#define MONO_FUNCTIONS_INITIALIZER \
    { "mono_string_to_utf8", 0, 0, USING_UNICODE|NO_CONTEXT, SpecialHookMonoString } \
  , { "mono_string_to_utf8_checked", 0, 0, USING_UNICODE|NO_CONTEXT, SpecialHookMonoString } \
  , { "mono_string_to_utf16", 0, 0, USING_UNICODE|NO_CONTEXT, SpecialHookMonoString } \
  , { "mono_string_intern", 0, 0, USING_UNICODE|NO_CONTEXT, SpecialHookMonoString } \
  , { "mono_string_is_interned", 0, 0, USING_UNICODE|NO_CONTEXT, SpecialHookMonoString } \
  , { "mono_marshal_string_to_utf16", 0, 0, USING_UNICODE|NO_CONTEXT, SpecialHookMonoString } \
  , { "mono_string_hash", 0, 0, USING_UNICODE, SpecialHookMonoString } \
  , { "mono_string_chars", 0, 0, USING_UNICODE, SpecialHookMonoString } \
  , { "mono_string_length", 0, 0, USING_UNICODE, SpecialHookMonoString } \
  , { "mono_utf8_from_external", 1, 0, USING_STRING|USING_UTF8, nullptr } \
  , { "mono_string_from_utf16", 1, 0, USING_UNICODE, nullptr } \
  , { "mono_string_new_utf16", 2, 3, USING_UNICODE, nullptr } \
  , { "mono_unicode_from_external", 1, 0, USING_UNICODE, nullptr } \
  , { "mono_unicode_to_external", 1, 0, USING_UNICODE, nullptr } \
  , { "mono_string_new", 2, 0, USING_STRING|USING_UTF8, nullptr } \
  , { "mono_string_new_len", 2, 3, USING_STRING|USING_UTF8, nullptr } \
  , { "mono_string_new_wrapper", 1, 0, USING_STRING|USING_UTF8, nullptr }

// EOF
