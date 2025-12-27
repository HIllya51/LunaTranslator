
#ifndef WINXP
#include <appmodel.h>
#include <roapi.h>
#include <Windows.Management.Deployment.h>
#include <Windows.Foundation.Collections.h>
#else
#include "../../xpundef/xp_winrt.hpp"
#include "../../xpundef/xp_appmodel.h"
#endif

#include "hstring.hpp"

using ABI::Windows::ApplicationModel::IPackage;
using ABI::Windows::ApplicationModel::IPackageId;
using ABI::Windows::ApplicationModel::Package;
using ABI::Windows::Foundation::Collections::IIterable;
using ABI::Windows::Foundation::Collections::IIterator;
using ABI::Windows::Management::Deployment::IPackageManager;
using ABI::Windows::Storage::IStorageFolder;
using ABI::Windows::Storage::IStorageItem;

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

DECLARE_API void FindPackages(void (*cb)(LPCWSTR, LPCWSTR), LPCWSTR checkid)
{
    CComPtr<IPackageManager> packageManager;
    CHECK_FAILURE_NORET(RoActivateInstance(AutoHString(RuntimeClass_Windows_Management_Deployment_PackageManager), reinterpret_cast<IInspectable **>(&packageManager)));

    CComPtr<IIterable<Package *>> packagesFoundRaw;
    CHECK_FAILURE_NORET(packageManager->FindPackagesByUserSecurityId(AutoHString(L""), &packagesFoundRaw));

    CComPtr<IIterator<Package *>> packagesFoundRaw_itor;
    CHECK_FAILURE_NORET(packagesFoundRaw->First(&packagesFoundRaw_itor));

    boolean fHasCurrent;
    CHECK_FAILURE_NORET(packagesFoundRaw_itor->get_HasCurrent(&fHasCurrent));
    while (fHasCurrent)
    {
        CComPtr<IPackage> package;
        CHECK_FAILURE_NORET(packagesFoundRaw_itor->get_Current(&package));
        CComPtr<IPackageId> packageid;
        CHECK_FAILURE_NORET(package->get_Id(&packageid));
        AutoHString strname;
        CHECK_FAILURE_NORET(packageid->get_Name(&strname));
        PCWSTR _name = strname;
        if (wcsstr(_name, checkid) == _name)
        {
            CComPtr<IStorageFolder> installpath;
            CHECK_FAILURE_NORET(package->get_InstalledLocation(&installpath));
            CComPtr<IStorageItem> item;
            CHECK_FAILURE_NORET(installpath.QueryInterface(&item));
            AutoHString str;
            item->get_Path(&str);
            cb(_name, str);
        }
        CHECK_FAILURE_NORET(packagesFoundRaw_itor->MoveNext(&fHasCurrent));
    }
}