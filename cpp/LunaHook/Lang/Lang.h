#pragma warning(push)
#pragma warning(disable: 4005)

#define English 0
#define Chinese 1
#define Russian 2
#define TradChinese 3

#include"en.h"

#if (LANGUAGE == Chinese)
#include"zh.h"
#endif
#if (LANGUAGE == Russian)
#include"ru.h"
#endif
#if (LANGUAGE == TradChinese)
#include"cht.h"
#endif


#pragma warning(pop)