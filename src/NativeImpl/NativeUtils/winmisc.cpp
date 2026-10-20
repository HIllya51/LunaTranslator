#include "../fileversion.hpp"

DECLARE_API bool QueryVersion(const wchar_t *exe, WORD *_1, WORD *_2, WORD *_3, WORD *_4)
{
    auto version = QueryVersion(exe);
    if (!version)
        return false;

    std::tie(*_1, *_2, *_3, *_4) = version.value();
    return true;
}

// 检查是否有窗口，有则重定向。
// 这个freopen是vcrt内部的东西，每个vcrt运行时必须独立重定向。
// 如果静态链接了exe，则exe内的freopen只会修改其内部的stdio，dll的vcrt无法受其影响。
#ifdef WIN10ABOVE
auto __ = []()
{
    if (GetConsoleWindow())
    {
        FILE *stream = nullptr;
        freopen_s(&stream, "CONOUT$", "w", stdout);
        freopen_s(&stream, "CONOUT$", "w", stderr);
    }
    return 0;
}();
#endif
