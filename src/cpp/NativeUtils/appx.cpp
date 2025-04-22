﻿
#ifndef WINXP
#include <appmodel.h>
#else
#define PACKAGE_FILTER_HEAD 0x00000010
extern "C"
{
    WINBASEAPI
    _Check_return_
        _Success_(return == ERROR_SUCCESS)
            _On_failure_(_Unchanged_(*count))
                _On_failure_(_Unchanged_(*bufferLength))
                    LONG
        WINAPI
        GetPackagesByPackageFamily(
            _In_ PCWSTR packageFamilyName,
            _Inout_ UINT32 *count,
            _Out_writes_opt_(*count) PWSTR *packageFullNames,
            _Inout_ UINT32 *bufferLength,
            _Out_writes_opt_(*bufferLength) WCHAR *buffer);
    WINBASEAPI
    _Success_(return == ERROR_SUCCESS)
        LONG
        WINAPI
        GetPackagePathByFullName(
            _In_ PCWSTR packageFullName,
            _Inout_ UINT32 *pathLength,
            _Out_writes_opt_(*pathLength) PWSTR path);
    WINBASEAPI
    _Check_return_
        _Success_(return == ERROR_SUCCESS)
            _On_failure_(_Unchanged_(*count))
                _On_failure_(_Unchanged_(*bufferLength))
                    LONG
        WINAPI
        FindPackagesByPackageFamily(
            _In_ PCWSTR packageFamilyName,
            _In_ UINT32 packageFilters,
            _Inout_ UINT32 *count,
            _Out_writes_opt_(*count) PWSTR *packageFullNames,
            _Inout_ UINT32 *bufferLength,
            _Out_writes_opt_(*bufferLength) WCHAR *buffer,
            _Out_writes_opt_(*count) UINT32 *packageProperties);
}
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