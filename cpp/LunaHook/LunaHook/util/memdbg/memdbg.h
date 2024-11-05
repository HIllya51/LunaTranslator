#ifndef _MEMDBG_H
#define _MEMDBG_H

// memdbg.h
// 4/20/2014 jichi

#ifndef MEMDBG_BEGIN_NAMESPACE
# define MEMDBG_BEGIN_NAMESPACE namespace MemDbg {
#endif
#ifndef MEMDBG_END_NAMESPACE
# define MEMDBG_END_NAMESPACE   } // MemDbg
#endif

MEMDBG_BEGIN_NAMESPACE

typedef unsigned char byte_t;
typedef unsigned long dword_t;

//typedef void *address_t; // LPVOID
//typedef const void *const_address_t; // LPCVOID

MEMDBG_END_NAMESPACE


#endif // _MEMDBG_H
