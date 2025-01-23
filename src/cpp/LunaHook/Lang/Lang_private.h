#include "Lang.h"
#include <unordered_map>
#include <string>
enum SUPPORT_LANG
{
    Chinese,
    TradChinese,
    English,
    Russian,
};
#define DEFINEFUNCTION(type, mp, ret)                  \
    const ret *langhelper::operator[](type langstring) \
    {                                                  \
        auto &&_ = mp[langstring];                     \
        auto &&__ = _.find(curr_lang);                 \
        if (__ == _.end())                             \
            __ = _.find(English);                      \
        return __->second;                             \
    }
