#ifndef MONOTYPE_H
#define MONOTYPE_H

// monotype.h
// 12/26/2014 jichi
// https://github.com/mono/mono/blob/master/mono/metadata/object.h

#include "mono/monoobject.h"

// Function typedefs
typedef MonoDomain *(* mono_object_get_domain_fun_t)(MonoObject *obj);

typedef MonoString *(* mono_string_new_utf16_fun_t)(MonoDomain *domain, const mono_unichar2 *text, int32_t len);

typedef char * (* mono_string_to_utf8_fun_t)(MonoString *string_obj);

#endif // MONOTYPE_H
