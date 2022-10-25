#pragma once
#ifndef CCMACRO_H
#define CCMACRO_H

// ccmacro.h
// 12/9/2011 jichi

#define CC_UNUSED(_var) (void)(_var)
#define CC_NOP          CC_UNUSED(0)

#if __GNUC__ > 2 || (__GNUC__ == 2 && __GNUC_MINOR__ >= 96)
# define CC_LIKELY(expr)    __builtin_expect(!!(expr), true)
# define CC_UNLIKELY(expr)  __builtin_expect(!!(expr), false)
#else
# define CC_LIKELY(x)   (x)
# define CC_UNLIKELY(x) (x)
#endif

#define CC_MIN(x, y)    ((x) < (y) ? (x) : (y))
#define CC_MAX(x, y)    ((x) < (y) ? (y) : (x))

#endif // CCMACRO_H
