
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
