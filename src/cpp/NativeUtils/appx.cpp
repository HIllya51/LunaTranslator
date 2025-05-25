
#ifndef WINXP
#include <appmodel.h>
#else
#include "../xpundef/xp_appmodel.h"
#endif
std::optional<std::wstring> FindPackage(const wchar_t *packageFamilyName)
{
    UINT32 count = 0;
    UINT32 bufferLength = 0;
    if (ERROR_INSUFFICIENT_BUFFER != FindPackagesByPackageFamily(
                                         packageFamilyName,
                                         PACKAGE_FILTER_HEAD, // 只返回主包（去掉此标志可获取所有包）
                                         &count,
                                         nullptr,
                                         &bufferLength,
                                         nullptr,
                                         nullptr))
        return {};
    if (!count)
        return {};
    auto buffer = std::make_unique<WCHAR[]>(bufferLength);
    auto packageFullNames = std::make_unique<PWSTR[]>(count);
    if (ERROR_SUCCESS != FindPackagesByPackageFamily(
                             packageFamilyName,
                             PACKAGE_FILTER_HEAD,
                             &count,
                             packageFullNames.get(),
                             &bufferLength,
                             buffer.get(), nullptr))
        return {};

    if (!count)
        return {};

    return packageFullNames[0];
}

std::optional<std::wstring> GetPackage(const wchar_t *packageFamilyName)
{
    UINT32 count = 0;
    UINT32 bufferLength = 0;
    if (ERROR_INSUFFICIENT_BUFFER != GetPackagesByPackageFamily(
                                         packageFamilyName,
                                         &count,
                                         nullptr,
                                         &bufferLength,
                                         nullptr))
        return {};
    if (!count)
        return {};
    auto buffer = std::make_unique<WCHAR[]>(bufferLength);
    auto packageFullNames = std::make_unique<PWSTR[]>(count);
    if (ERROR_SUCCESS != GetPackagesByPackageFamily(
                             packageFamilyName,
                             &count,
                             packageFullNames.get(),
                             &bufferLength,
                             buffer.get()))
        return {};

    if (!count)
        return {};

    return packageFullNames[0];
}
std::optional<std::wstring> GetPackagePath(const wchar_t *packageFullName)
{
    UINT32 l = 0;
    if (ERROR_INSUFFICIENT_BUFFER != GetPackagePathByFullName(packageFullName, &l, nullptr))
        return {};
    auto buffer = std::make_unique<WCHAR[]>(l);
    if (ERROR_SUCCESS != GetPackagePathByFullName(packageFullName, &l, buffer.get()))
        return {};
    return buffer.get();
}
DECLARE_API void GetPackagePathByPackageFamily(const wchar_t *packageFamilyName, void (*cb)(LPCWSTR))
{
    auto fn = FindPackage(packageFamilyName);
    // auto fn = GetPackage(packageFamilyName);
    if (!fn)
        return;
    fn = GetPackagePath(fn.value().c_str());
    if (!fn)
        return;
    cb(fn.value().c_str());
}