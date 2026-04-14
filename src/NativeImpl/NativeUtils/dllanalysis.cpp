#include "dllanalysis.hpp"

DECLARE_API void AnalysisDllImports(LPCWSTR file, void (*cb)(const char *, DWORD, bool))
{
    auto &&[import, delay] = importAnalysis(file);
    for (auto &&[fn, off] : import)
    {
        cb(fn.c_str(), off, true);
    }
    for (auto &&[fn, off] : delay)
    {
        cb(fn.c_str(), off, false);
    }
}

DECLARE_API void AnalysisDllExports(LPCWSTR file, void (*cb)(const char *))
{
    auto &&_ = exportAnalysis(file);
    for (auto &&name : _)
    {
        // Oridinal， RVA就先不输出了，反正用不着。
        cb(name.c_str());
    }
}