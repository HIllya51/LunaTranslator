#ifndef EBYUTIL_H
#define EBYUTIL_H

#ifdef _DEBUG
#include "assert.h"
#define e_assert(expr) assert(expr)
#define en_assert(expr) assert(expr)
#else
#define e_assert(expr)                                                          \
  do                                                                            \
  {                                                                             \
    if (!(expr))                                                                \
    {                                                                           \
      napi_throw_error(env, "EBY001", "assertion e_assert(" #expr ") failed."); \
      return;                                                                   \
    };                                                                          \
  } while (0)
#define en_assert(expr)                                                          \
  do                                                                             \
  {                                                                              \
    if (!(expr))                                                                 \
    {                                                                            \
      napi_throw_error(env, "EBY001", "assertion en_assert(" #expr ") failed."); \
      return NULL;                                                               \
    };                                                                           \
  } while (0)
#endif

#ifdef _DEBUG
#define Dprintf(a, ...)                                          \
  do                                                             \
  {                                                              \
    printf("\x1b[1;36m[C++ DEBUG]\x1b[0m " a "\n", __VA_ARGS__); \
  } while (0)
#else
#define Dprintf(a, ...) \
  do                    \
  {                     \
  } while (0)
#endif

#define Eprintf(a, ...)                                               \
  do                                                                  \
  {                                                                   \
    fprintf(stderr, "\x1b[1;31m[ERROR]\x1b[0m " a "\n", __VA_ARGS__); \
  } while (0)

#define _____coffee(milk) #milk
#define _____applepie(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t) \
  _____coffee(j##a##l##f##k##n##i##g##h##t##s##q##r##c##o##d##e##b##m##p)

#define EBY_SEED_A _____applepie(R, 2, p, b, H, J, I, W, A, O, C, X, a, 6, D, l, K, D, U, A)
#define EBY_SEED_B _____applepie(b, R, Q, 6, 1, D, e, Y, 7, q, 1, I, E, A, T, 4, Q, q, P, a)
#define EBY_SEED_C _____applepie(q, M, t, d, C, N, e, l, 8, N, 1, K, C, 4, m, U, O, 2, u, p)
#define EBY_SEED_D _____applepie(2, Y, Z, 0, c, w, 2, N, 1, b, 7, 4, b, D, T, M, K, 8, 1, 5)
#define EBY_SEED_E _____applepie(D, j, Y, l, J, 1, Z, 5, g, L, 7, h, C, E, X, m, V, 7, S, g)

#endif // EBYUTIL_H
