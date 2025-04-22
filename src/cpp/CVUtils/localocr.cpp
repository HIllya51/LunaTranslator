
#include "dbcrnn.hpp"

DECLARE_API OcrLite *OcrInit(const wchar_t *szDetModel, const wchar_t *szRecModel, const wchar_t *szKeyPath, int nThreads)
{
    OcrLite *pOcrObj = nullptr;
    try
    {
        pOcrObj = new OcrLite(szDetModel, szRecModel, szKeyPath, nThreads);
    }
    catch (...)
    {
    }
    if (pOcrObj)
    {
        return pOcrObj;
    }
    else
    {
        return nullptr;
    }
}

DECLARE_API void OcrDetect(OcrLite *pOcrObj, const cv::Mat *mat,
                           Directional mode, void (*cb)(float, float, float, float, float, float, float, float, const char *))
{
    if (!pOcrObj)
        return;

    try
    {
        auto result = pOcrObj->detect(*mat, 50, 0.1, 0.1, 2.0, mode);

        for (auto item : result)
        {
            cb(item.first[0].x, item.first[0].y,
               item.first[1].x, item.first[1].y,
               item.first[2].x, item.first[2].y,
               item.first[3].x, item.first[3].y,
               item.second.c_str());
        }
    }
    catch (...)
    {
    }
}

DECLARE_API void OcrDestroy(OcrLite *pOcrObj)
{
    if (pOcrObj)
        delete pOcrObj;
}

static std::optional<std::wstring> SearchDllPath(const std::wstring &dll)
{
    auto len = SearchPathW(NULL, dll.c_str(), NULL, 0, NULL, NULL);
    if (!len)
        return {};
    std::wstring buff;
    buff.resize(len);
    len = SearchPathW(NULL, dll.c_str(), NULL, len, buff.data(), NULL);
    if (!len)
        return {};
    return std::move(buff);
}
extern "C" bool QueryVersion(const wchar_t *exe, WORD *_1, WORD *_2, WORD *_3, WORD *_4);
static std::optional<std::tuple<DWORD, DWORD, DWORD, DWORD>> QueryVersion(const std::optional<std::wstring> &exe)
{
    if (!exe)
        return {};
    WORD _1, _2, _3, _4;
    if (!QueryVersion(exe.value().c_str(), &_1, &_2, &_3, &_4))
        return {};
    std::wcout << _1 << L"," << _2 << L"," << _3 << L"," << _4 << L"\t" << exe.value() << L"\n";
    return std::make_tuple(_1, _2, _3, _4);
}

DECLARE_API bool OcrLoadRuntime()
{
    HMODULE hmodule;
    GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS, (LPCWSTR)&OcrLoadRuntime, &hmodule);
    if (GetModuleHandleW(L"OrtWrapper.dll"))
        return true;
    // 尝试加载系统onnxruntime，版本更高，有directml优化，速度稍快一丢丢
    auto sysonnx = SearchDllPath(L"onnxruntime.dll");
    auto ver = QueryVersion(sysonnx);
    WCHAR path[MAX_PATH];
    GetModuleFileNameW(hmodule, path, MAX_PATH);
    auto currdir = std::filesystem::path(path).parent_path();
    auto myonnx = (currdir / "onnxruntime.dll").wstring();
    auto vermy = QueryVersion(myonnx);
    // 最多尝试系统onnxruntime到v1.20.1版本，v1.21.0开始会不兼容。
    // https://github.com/microsoft/onnxruntime/releases/tag/v1.21.0
    // All the prebuilt Windows packages now require VC++ Runtime version >= 14.40(instead of 14.38). If your VC++ runtime version is lower than that, you may see a crash when ONNX Runtime was initializing. See https://github.com/microsoft/STL/wiki/Changelog#vs-2022-1710 for more details.
    // 不过实测在更古老py37(14.00)上是没问题的，但在py311(14.38)或pyqt(14.26)上确实会崩溃，保险起见不要加载。
    auto usewhichonnxruntime = (((ver >= vermy) && (ver < std::make_tuple(1, 21, 0, 0)))) ? sysonnx : myonnx;
    if (!usewhichonnxruntime)
        return false;
    std::wcout << usewhichonnxruntime.value() << L"\n";
    return LoadLibrary(usewhichonnxruntime.value().c_str()) && LoadLibrary((currdir / "OrtWrapper.dll").wstring().c_str());
}