#include "Lang.h"
#include <unordered_map>
#include <string>

#define DEFINEFUNCTION(type, mp, ret, which)                         \
    const ret *langhelper::operator[](type langstring)               \
    {                                                                \
        auto &&_ = mp[langstring];                                   \
        return _.get();                                              \
    }                                                                \
    std::unordered_map<type, i18nString<ret>> &langhelper::##which() \
    {                                                                \
        return mp;                                                   \
    }
