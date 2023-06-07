# YY-Thunks Thunks 清单

此表展示了YY-Thunks（鸭船）可以解决的函数不存在问题，欢迎大家扩充！

> 开头带`*`的函数并不建议使用，仅用于编译通过处理，如果使用可能导致老版本系统无法充分发挥性能。

## api-ms-win-core-path-l1-1-0.dll
| 函数                                       | Fallback
| ----                                       | -----------
| PathIsUNCEx                                | 内部实现。
| PathCchIsRoot                              | 内部实现。
| PathCchAddBackslashEx                      | 内部实现。
| PathCchAddBackslash                        | 调用PathCchAddBackslashEx。
| PathCchRemoveBackslashEx                   | 内部实现。
| PathCchRemoveBackslash                     | 调用PathCchRemoveBackslashEx。
| PathCchSkipRoot                            | 内部实现。
| PathCchStripToRoot                         | 内部实现。
| PathCchRemoveFileSpec                      | 内部实现。
| PathCchFindExtension                       | 内部实现。
| PathCchAddExtension                        | 调用PathCchFindExtension。
| PathCchRenameExtension                     | 调用PathCchFindExtension。
| PathCchRemoveExtension                     | 调用PathCchFindExtension。
| PathCchCanonicalizeEx                      | 不存在时，内部实现。
| PathCchCanonicalize                        | 调用PathCchCanonicalizeEx。
| PathCchCombineEx                           | 内部实现。
| PathCchCombine                             | 调用PathCchCombineEx。
| PathCchAppendEx                            | 调用PathCchCombineEx。
| PathCchAppend                              | 调用PathCchAppendEx。
| PathCchStripPrefix                         | 内部实现。
| PathAllocCombine                           | 不存在时，调用PathCchCombineEx。
| PathAllocCanonicalize                      | 不存在时，调用PathCchCanonicalizeEx。

## api-ms-win-core-winrt-l1-1-0.dll
| 函数                                       | Fallback
| ----                                       | -----------
| RoInitialize                               | 不存在时，调用 CoInitializeEx。
| RoUninitialize                             | 不存在时，调用 CoUninitialize。
| RoActivateInstance                         | 不存在时，返回 E_NOTIMPL。
| RoRegisterActivationFactories              | 不存在时，返回 E_NOTIMPL。
| RoRevokeActivationFactories                | 不存在时，什么也不做。
| RoGetActivationFactory                     | 不存在时，返回 E_NOTIMPL。
| RoRegisterForApartmentShutdown             | 不存在时，返回 E_NOTIMPL。
| RoUnregisterForApartmentShutdown           | 不存在时，返回 E_NOTIMPL。
| RoGetApartmentIdentifier                   | 不存在时，返回 E_NOTIMPL。

## api-ms-win-core-winrt-error-l1-1-0.dll
| 函数                                       | Fallback
| ----                                       | -----------
| RoOriginateError                           | 不存在时，返回 FALSE.
| RoOriginateErrorW                          | 不存在时，返回 FALSE.

## api-ms-win-core-winrt-string-l1-1-0.dll
| 函数                                       | Fallback
| ----                                       | -----------
| WindowsCreateString                        | 不存在时，返回 E_NOTIMPL。
| WindowsCreateStringReference               | 不存在时，返回 E_NOTIMPL。
| WindowsDeleteString                        | 不存在时，返回 E_NOTIMPL。
| WindowsDuplicateString                     | 不存在时，返回 E_NOTIMPL。
| WindowsGetStringLen                        | 不存在时，返回 E_NOTIMPL。
| WindowsGetStringRawBuffer                  | 不存在时，返回 E_NOTIMPL。
| WindowsIsStringEmpty                       | 不存在时，返回 E_NOTIMPL。
| WindowsStringHasEmbeddedNull               | 不存在时，返回 E_NOTIMPL。
| WindowsCompareStringOrdinal                | 不存在时，返回 E_NOTIMPL。

## advapi32.dll
| 函数                                       | Fallback
| ----                                       | -----------
| RegDeleteKeyExW(A)                         | 不存在时，调用RegDeleteKeyW(A)。
| RegSetKeyValueW(A)                         | 调用RegCreateKeyExW(A)以及RegSetValueExW(A)。
| RegDeleteKeyValueW(A)                      | 调用RegOpenKeyExW(A)以及RegDeleteValueW(A)。
| RegDeleteTreeW(A)                          | 调用SHDeleteKeyW(A)。
| RegGetValueW(A)                            | 不存在时，调用RegQueryValueExW(A)。
| RegCopyTreeW(A)                            | 不存在时，调用SHCopyKeyW(A)。
| EventSetInformation                        | 不存在时，返回ERROR_NOT_SUPPORTED。

## bcrypt.dll
| 函数                                       | Fallback
| ----                                       | -----------
| BCryptOpenAlgorithmProvider                | 内部实现。
| BCryptCloseAlgorithmProvider               | 内部实现。
| BCryptGenRandom                            | 不存在时调用，RtlGenRandom。

## bluetoothapis.dll
| 函数                                       | Fallback
| ----                                       | -----------
| BluetoothGATTGetCharacteristicValue        | 不存在时，返回ERROR_NOT_SUPPORTED。
| BluetoothGATTGetCharacteristics            | 不存在时，返回ERROR_NOT_SUPPORTED。
| BluetoothGATTGetDescriptors                | 不存在时，返回ERROR_NOT_SUPPORTED。
| BluetoothGATTGetServices                   | 不存在时，返回ERROR_NOT_SUPPORTED。
| BluetoothGATTRegisterEvent                 | 不存在时，返回ERROR_NOT_SUPPORTED。
| BluetoothGATTSetCharacteristicValue        | 不存在时，返回ERROR_NOT_SUPPORTED。
| BluetoothGATTSetDescriptorValue            | 不存在时，返回ERROR_NOT_SUPPORTED。

## iphlpapi.dll
| 函数                                       | Fallback
| ----                                       | -----------
| GetIfTable2                                | 不存在时调用，GetIfTable，并使用HeapAlloc申请内存。
| GetIfTable2Ex                              | 不存在时调用，GetIfTable，并使用HeapAlloc申请内存。
| GetIfEntry2                                | 不存在时调用，GetIfEntry。
| GetIfEntry2Ex                              | 不存在时调用，GetIfEntry2。
| FreeMibTable                               | 不存在时调用，HeapFree。

## kernel32.dll
| 函数                                       | Fallback
| ----                                       | -----------
| DecodePointer                              | 不存在时，返回指针本身。
| EncodePointer                              | 不存在时，返回指针本身。
| Wow64DisableWow64FsRedirection             | 不存在时，返回FALSE，并设置 LastError = ERROR_INVALID_FUNCTION。
| Wow64RevertWow64FsRedirection              | 不存在时，返回FALSE，并设置 LastError = ERROR_INVALID_FUNCTION。
| Wow64EnableWow64FsRedirection              | 不存在时，返回FALSE，并设置 LastError = ERROR_INVALID_FUNCTION。
| IsWow64Process2                            | 不存在时，调用IsWow64Process。
| IsWow64GuestMachineSupported               | 不存在时，调用GetNativeSystemInfo。
| GetTickCount64                             | 不存在时，调用GetTickCount。
| GetSystemTimePreciseAsFileTime             | 不存在时，调用GetSystemTimeAsFileTime。
| InitializeCriticalSectionEx                | 不存在时，调用InitializeCriticalSectionAndSpinCount。
| InitOnceInitialize                         | 初始化为 INIT_ONCE_STATIC_INIT。
| InitOnceBeginInitialize                    | 不存在时，调用NtWaitForKeyedEvent。
| InitOnceComplete                           | 不存在时，调用NtReleaseKeyedEvent。
| InitOnceExecuteOnce                        | 不存在时，调用NtWaitForKeyedEvent以及NtReleaseKeyedEvent。
| LocaleNameToLCID                           | 不存在时，查LocaleNameToLcidTable。
| LCIDToLocaleName                           | 不存在时，查LcidToLocaleNameTable。
| GetLocaleInfoEx                            | 不存在时，调用GetLocaleInfoW。
| GetDateFormatEx                            | 不存在时，调用GetDateFormatW。
| GetTimeFormatEx                            | 不存在时，调用GetTimeFormatW。
| GetNumberFormatEx                          | 不存在时，调用GetNumberFormatW。
| GetCurrencyFormatEx                        | 不存在时，调用GetCurrencyFormatW。
| GetUserDefaultLocaleName                   | 不存在时，调用LCIDToLocaleName。
| GetSystemDefaultLocaleName                 | 不存在时，调用LCIDToLocaleName。
| EnumCalendarInfoExEx                       | 不存在时，调用EnumCalendarInfoExW。
| EnumDateFormatsExEx                        | 不存在时，调用EnumDateFormatsExW。
| LCMapStringEx                              | 不存在时，调用LCMapStringW。
| GetFileInformationByHandleEx               | 不存在时，调用NtQueryInformationFile 或者 NtQueryDirectoryFile。
| SetFileInformationByHandle                 | 不存在时，调用NtSetInformationFile。
| GetFinalPathNameByHandleW(A)               | 不存在时，调用NtQueryObject以及NtQueryInformationFile。
| GetLogicalProcessorInformation             | 不存在时，返回FALSE，并设置 LastError = ERROR_INVALID_FUNCTION。
| GetLogicalProcessorInformationEx           | 不存在时，调用GetLogicalProcessorInformation。
| GetNumaHighestNodeNumber                   | 不存在时，返回0。
| RaiseFailFastException                     | 不存在时，调用TerminateProcess。
| GetThreadId                                | 不存在时，调用NtQueryInformationThread。
| GetProcessIdOfThread                       | 不存在时，调用NtQueryInformationThread。
| GetProcessId                               | 不存在时，调用NtQueryInformationProcess。
| QueryThreadCycleTime                       | 不存在时，调用GetThreadTimes。
| QueryProcessCycleTime                      | 不存在时，调用GetProcessTimes。
| K32EnumProcessModules                      | 调用EnumProcessModules。
| K32EnumProcessModulesEx                    | 调用EnumProcessModulesEx。
| K32GetModuleBaseNameW(A)                   | 调用GetModuleBaseNameW(A)。
| K32GetModuleFileNameExW(A)                 | 调用K32GetModuleFileNameExW(A)。
| K32EmptyWorkingSet                         | 调用EmptyWorkingSet。
| K32QueryWorkingSet                         | 调用QueryWorkingSet。
| K32QueryWorkingSetEx                       | 调用QueryWorkingSetEx。
| K32InitializeProcessForWsWatch             | 调用InitializeProcessForWsWatch。
| K32GetWsChanges                            | 调用GetWsChanges。
| K32GetWsChangesEx                          | 调用GetWsChangesEx。
| K32GetMappedFileNameW(A)                   | 调用GetMappedFileNameW(A)。
| K32EnumDeviceDrivers                       | 调用EnumDeviceDrivers。
| K32GetDeviceDriverBaseNameW(A)             | 调用GetDeviceDriverBaseNameW(A)。
| K32GetDeviceDriverFileNameW(A)             | 调用GetDeviceDriverFileNameW(A)。
| K32GetPerformanceInfo                      | 调用GetPerformanceInfo。
| K32EnumPageFilesW(A)                       | 调用EnumPageFilesW(A)。
| K32GetProcessImageFileNameW(A)             | 调用GetProcessImageFileNameW(A)。
| QueryFullProcessImageNameW(A)              | 不存在时，调用GetProcessImageFileNameW(A) 或者 GetModuleFileNameExW(A)。
| CreateFile2                                | 不存在时，调用CreateFileW。
| CreateEventExW(A)                          | 不存在时，调用CreateEventW(A)。
| CreateMutexExW(A)                          | 不存在时，调用CreateMutexW(A)。
| CreateSemaphoreExW                         | 不存在时，调用CreateSemaphoreW。
| CreateWaitableTimerExW                     | 不存在时，调用CreateWaitableTimerW。
| InterlockedCompareExchange64               | 调用内部函数_InterlockedCompareExchange64。
| SetThreadErrorMode                         | 不存在时，调用SetErrorMode。
| GetThreadErrorMode                         | 不存在时，调用GetErrorMode。
| GetErrorMode                               | 不存在时，调用NtQueryInformationProcess。
| InitializeSRWLock                          | 初始化为 RTL_SRWLOCK_INIT。
| AcquireSRWLockExclusive                    | 不存在时，调用NtWaitForKeyedEvent。
| TryAcquireSRWLockExclusive                 | 不存在时，调用InterlockedBitTestAndSet(64)。
| ReleaseSRWLockExclusive                    | 不存在时，调用NtReleaseKeyedEvent。
| AcquireSRWLockShared                       | 不存在时，调用NtWaitForKeyedEvent。
| TryAcquireSRWLockShared                    | 不存在时，调用InterlockedCompareExchange。
| ReleaseSRWLockShared                       | 不存在时，调用NtReleaseKeyedEvent。
| InitializeConditionVariable                | 初始化为 CONDITION_VARIABLE_INIT。
| SleepConditionVariableCS                   | 不存在时，调用NtWaitForKeyedEvent。
| SleepConditionVariableSRW                  | 不存在时，调用NtWaitForKeyedEvent。
| WakeConditionVariable                      | 不存在时，调用NtReleaseKeyedEvent。
| WakeAllConditionVariable                   | 不存在时，调用NtReleaseKeyedEvent。
| InitializeSynchronizationBarrier           | 不存在时，调用CreateEvent。
| EnterSynchronizationBarrier                | 不存在时，调用WaitForSingleObject。
| DeleteSynchronizationBarrier               | 不存在时，调用CloseHandle。
| WaitOnAddress                              | 不存在时，调用NtWaitForKeyedEvent。警告，此函数请勿跨模块使用！！！
| WakeByAddressSingle                        | 不存在时，调用NtReleaseKeyedEvent。警告，此函数请勿跨模块使用！！！
| WakeByAddressAll                           | 不存在时，调用NtReleaseKeyedEvent。警告，此函数请勿跨模块使用！！！
| *GetCurrentProcessorNumber                 | 不存在时，返回0。
| *GetCurrentProcessorNumberEx               | 不存在时，调用GetCurrentProcessorNumber。
| *GetNumaNodeProcessorMask                  | 不存在时，假定所有CPU都在当前Numa。
| *GetNumaNodeProcessorMaskEx                | 不存在时，调用GetNumaNodeProcessorMask。
| *SetThreadGroupAffinity                    | 不存在时，调用SetThreadAffinityMask。
| *CancelIoEx                                | 不存在时，调用CancelIo（会把此句柄的所有IO操作取消掉！）。
| OpenFileById                               | 不存在时，调用NtCreateFile。
| CreateSymbolicLinkW(A)                     | 不存在时，返回FALSE，并设置 LastError = ERROR_INVALID_FUNCTION。
| ReOpenFile                                 | 不存在时，调用NtCreateFile。
| CompareStringEx                            | 不存在时，调用CompareStringW。
| CompareStringOrdinal                       | 不存在时，使用内置UnicodeCaseTableData实现。
| SetFilePointerEx                           | 不存在时，调用SetFilePointer。
| GetModuleHandleExW(A)                      | 不存在时，调用GetModuleHandleW(A)。
| WTSGetActiveConsoleSessionId               | 不存在时，直接返回 0。
| GetNativeSystemInfo                        | 不存在时，调用GetSystemInfo。
| InitializeSListHead                        | 直接初始化为 0。
| InterlockedFlushSList                      | 不存在时，调用lock cmpxchg8b指令。
| QueryDepthSList                            | 不存在时，直接返回Depth。
| InterlockedPushEntrySList                  | 不存在时，调用lock cmpxchg8b指令。
| InterlockedPopEntrySList                   | 不存在时，调用lock cmpxchg8b指令。
| GetNumaProximityNodeEx                     | 不存在时，调用GetNumaProximityNode。
| GetNumaProcessorNode                       | 不存在时，假定所有CPU都在节点 0。
| GetNumaNodeNumberFromHandle                | 不存在时，假定所有CPU都在节点 0。
| GetNumaProcessorNodeEx                     | 不存在时，调用 GetNumaProcessorNode 。
| GetNumaAvailableMemoryNode                 | 不存在时，假定所有内存都属于节点0 。
| GetNumaAvailableMemoryNodeEx               | 不存在时，调用 GetNumaAvailableMemoryNode 。
| GetNumaProximityNode                       | 不存在时，假定都是节点0 。
| AllocateUserPhysicalPagesNuma              | 不存在时，调用 AllocateUserPhysicalPages 。
| MapViewOfFileExNuma                        | 不存在时，调用 MapViewOfFileEx。
| VirtualAllocExNuma                         | 不存在时，调用 VirtualAllocEx 。
| CreateFileMappingNumaW(A)                  | 不存在时，调用 CreateFileMappingW(A) 。
| GetMaximumProcessorCount                   | 不存在时，调用 GetSystemInfo 。
| GetActiveProcessorCount                    | 不存在时，调用 GetSystemInfo 。
| GetActiveProcessorGroupCount               | 不存在时，假定为1 。
| GetMaximumProcessorGroupCount              | 不存在时，假定为1 。
| GetMemoryErrorHandlingCapabilities         | 不存在时，直接报告不支持任何特性。
| VirtualAllocFromApp                        | 不存在时，调用 VirtualAlloc 。
| VirtualAlloc2                              | 不存在时，调用 VirtualAllocExNuma 以及 VirtualAllocEx 。
| VirtualAlloc2FromApp                       | 不存在时，调用 VirtualAllocExNuma 以及 VirtualAllocEx 。
| CreateFileMappingFromApp                   | 不存在时，调用 CreateFileMappingW 。
| CreateFileMapping2                         | 不存在时，调用 CreateFileMappingNumaW 以及 CreateFileMappingW 。
| MapViewOfFileFromApp                       | 不存在时，调用 MapViewOfFile 。
| UnmapViewOfFileEx                          | 不存在时，调用 UnmapViewOfFile 。
| VirtualProtectFromApp                      | 不存在时，调用 VirtualProtect 。
| OpenFileMappingFromApp                     | 不存在时，调用 OpenFileMappingW 。
| CreateThreadpoolWork                       | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| CloseThreadpoolWork                        | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| SubmitThreadpoolWork                       | 不存在时，调用QueueUserWorkItem。警告，此函数请勿跨模块使用！！！
| WaitForThreadpoolWorkCallbacks             | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| CreateThreadpoolTimer                      | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| CloseThreadpoolTimer                       | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| SetThreadpoolTimer                         | 不存在时，调用QueueTimer。警告，此函数请勿跨模块使用！！！
| SetEventWhenCallbackReturns                | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| ReleaseSemaphoreWhenCallbackReturns        | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| ReleaseMutexWhenCallbackReturns            | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| LeaveCriticalSectionWhenCallbackReturns    | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| FreeLibraryWhenCallbackReturns             | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| WaitForThreadpoolTimerCallbacks            | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| TrySubmitThreadpoolCallback                | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| CreateThreadpoolWait                       | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| CloseThreadpoolWait                        | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| SetThreadpoolWait                          | 不存在时，调用RegisterWaitForSingleObject。警告，此函数请勿跨模块使用！！！
| WaitForThreadpoolWaitCallbacks             | 不存在时，内部实现。警告，此函数请勿跨模块使用！！！
| FlushProcessWriteBuffers                   | 不存在时，调用VirtualProtect。
| FlsAlloc                                   | 不存在时，使用Tls实现。警告，此函数请勿跨模块使用！！！
| FlsFree                                    | 不存在时，使用Tls实现。警告，此函数请勿跨模块使用！！！
| FlsGetValue                                | 不存在时，使用Tls实现。警告，此函数请勿跨模块使用！！！
| FlsSetValue                                | 不存在时，使用Tls实现。警告，此函数请勿跨模块使用！！！
| IsThreadAFiber                             | 不存在时，调用 GetCurrentFiber。
| ConvertThreadToFiberEx                     | 不存在时，调用 ConvertThreadToFiber。
| GetDynamicTimeZoneInformation              | 不存在时，调用 GetTimeZoneInformation。
| SetDynamicTimeZoneInformation              | 不存在时，调用 SetTimeZoneInformation。
| GetProductInfo                             | 不存在时，调用 GetVersionExW。
| EnumSystemLocalesEx                        | 不存在时，调用 EnumSystemLocalesW。
| GetThreadPreferredUILanguages              | 不存在时，调用 GetThreadLocale、GetUserDefaultLangID以及GetSystemDefaultLangID。
| GetThreadUILanguage                        | 不存在时，调用 GetThreadLocale。
| ResolveLocaleName                          | 不存在时，调用 LocaleNameToLCID以及LCIDToLocaleName。
| InitializeProcThreadAttributeList          | 不存在时，内部实现。
| DeleteProcThreadAttributeList              | 不存在时，内部实现。
| UpdateProcThreadAttribute                  | 不存在时，内部实现。PROC_THREAD_ATTRIBUTE_PARENT_PROCESS与PROC_THREAD_ATTRIBUTE_HANDLE_LIST特性会被忽略处理。
| GetLargePageMinimum                        | 不存在时，假定为0 。
| SetThreadStackGuarantee                    | 不存在时，调用VirtualAlloc。
| SetCoalescableTimer                        | 不存在时，调用SetTimer。
| EnumResourceLanguagesExW(A)                | 不存在时，调用EnumResourceLanguagesW(A)。
| DiscardVirtualMemory                       | 不存在时，调用VirtualAlloc MEM_RESET。
| OfferVirtualMemory                         | 不存在时，返回ERROR_SUCCESS。
| ReclaimVirtualMemory                       | 不存在时，返回ERROR_SUCCESS。
| PrefetchVirtualMemory                      | 不存在时，返回ERROR_SUCCESS。
| GetProcessMitigationPolicy                 | 不存在时，调用NtQueryInformationProcess。
| SetProcessMitigationPolicy                 | 不存在时，调用NtSetInformationProcess。
| SetProcessInformation                      | 不存在时，调用NtSetInformationProcess。
| SetThreadInformation                       | 不存在时，调用NtSetInformationThread。
| PowerCreateRequest                         | 不存在时，内部实现。
| PowerSetRequest                            | 不存在时，调用 SetThreadExecutionState。
| PowerClearRequest                          | 不存在时，调用 SetThreadExecutionState。

## mfplat.dll
| 函数                                       | Fallback
| ----                                       | -----------
| MFCreateDXGIDeviceManager                  | 不存在时，返回E_NOTIMPL。
| MFCreateDXGISurfaceBuffer                  | 不存在时，返回E_NOTIMPL。
| MFLockDXGIDeviceManager                    | 不存在时，返回E_NOTIMPL。
| MFUnlockDXGIDeviceManager                  | 不存在时，返回E_NOTIMPL。

## netapi32.dll
| 函数                                       | Fallback
| ----                                       | -----------
| NetGetAadJoinInformation                   | 不存在时，始终认为没有加入 Azure AD 帐户 账号。
| NetFreeAadJoinInformation                  | 不存在时，什么也不做。

## ole32.dll
| 函数                                       | Fallback
| ----                                       | -----------
| CoGetApartmentType                         | 不存在时，调用IComThreadingInfo。

## pdh.dll
| 函数                                       | Fallback
| ----                                       | -----------
| PdhAddEnglishCounterW(A)                   | 不存在时，调用PdhAddCounterW(A)。

## powrprof.dll
| 函数                                       | Fallback
| ----                                       | -----------
| PowerDeterminePlatformRole                 | 不存在时，返回PlatformRoleDesktop。
| PowerDeterminePlatformRoleEx               | 不存在时，调用PlatformRoleDesktop。
| PowerRegisterSuspendResumeNotification     | 不存在时，使用窗口模拟。
| PowerUnregisterSuspendResumeNotification   | 内部实现。

## psapi.dll
| 函数                                       | Fallback
| ----                                       | -----------
| EnumProcessModulesEx                       | 不存在时，调用EnumProcessModules。
| GetWsChangesEx                             | 不存在时，调用GetWsChanges。
| *QueryWorkingSetEx                         | 不存在时，返回FALSE，并设置 LastError = ERROR_INVALID_FUNCTION。

## setupapi.dll
| 函数                                       | Fallback
| ----                                       | -----------
| SetupDiGetDevicePropertyW                  | 不存在时，调用SetupDiGetDeviceRegistryPropertyW。
| SetupDiSetDevicePropertyW                  | 不存在时，调用SetupDiSetDeviceRegistryPropertyW。
| SetupDiGetClassPropertyW                   | 不存在时，调用SetupDiGetClassRegistryPropertyW。
| SetupDiGetClassPropertyExW                 | 不存在时，调用SetupDiGetClassRegistryPropertyW。
| SetupDiSetClassPropertyW                   | 不存在时，调用SetupDiSetClassRegistryPropertyW。
| SetupDiSetClassPropertyExW                 | 不存在时，调用SetupDiSetClassRegistryPropertyW。

## shcore.dll
| 函数                                       | Fallback
| ----                                       | -----------
| GetDpiForMonitor                           | 不存在时，调用GetDeviceCaps。
| SetProcessDpiAwareness                     | 不存在时，调用SetProcessDPIAware。
| SetProcessDPIAware                         | 不存在时，直接返回 TRUE。

## shell32.dll
| 函数                                       | Fallback
| ----                                       | -----------
| SHGetKnownFolderPath                       | 不存在时，调用SHGetFolderPathW。
| SHSetKnownFolderPath                       | 不存在时，调用SHSetFolderPathW。
| SHGetKnownFolderIDList                     | 不存在时，调用SHGetFolderLocation。
| SHBindToFolderIDListParent                 | 不存在时，调用IShellFolder。
| SHBindToFolderIDListParentEx               | 不存在时，调用IShellFolder。
| SHBindToObject                             | 不存在时，调用IShellFolder。
| SHCreateItemFromIDList                     | 不存在时，调用IShellItem。
| SHCreateItemWithParent                     | 不存在时，调用IShellItem。
| SHCreateItemFromRelativeName               | 不存在时，调用IShellItem。
| SHGetNameFromIDList                        | 不存在时，调用IShellItem。
| SHCreateShellItem                          | 不存在时，调用IShellItem。
| SHCreateItemFromParsingName                | 不存在时，调用SHParseDisplayName。

## shlwapi.dll
| 函数                                       | Fallback
| ----                                       | -----------
| StrToInt64ExW(A)                           | 不存在时，手工解析字符串。

## user32.dll
| 函数                                       | Fallback
| ----                                       | -----------
| IsWow64Process                             | 不存在时，返回TRUE，并设置 `*Wow64Process = FALSE`。
| SetProcessDpiAwarenessContext              | 不存在时，调用SetProcessDpiAwareness。
| GetDpiForSystem                            | 不存在时，调用GetDeviceCaps。
| GetDpiForWindow                            | 不存在时，调用GetDpiForMonitor。
| GetSystemMetricsForDpi                     | 不存在时，调用GetSystemMetrics。
| AdjustWindowRectExForDpi                   | 不存在时，调用AdjustWindowRectEx。
| SystemParametersInfoForDpi                 | 不存在时，调用SystemParametersInfoW。
| RegisterSuspendResumeNotification          | 不存在时，使用窗口模拟。
| UnregisterSuspendResumeNotification        | 不存在时，内部实现。

## userenv.dll
| 函数                                       | Fallback
| ----                                       | -----------
| CreateAppContainerProfile                  | 不存在时，返回E_NOTIMPL。
| DeleteAppContainerProfile                  | 不存在时，返回E_NOTIMPL。
| DeriveAppContainerSidFromAppContainerName  | 不存在时，返回E_NOTIMPL。
| GetAppContainerFolderPath                  | 不存在时，返回E_NOTIMPL。
| GetAppContainerRegistryLocation            | 不存在时，返回E_NOTIMPL。

## version.dll
| 函数                                       | Fallback
| ----                                       | -----------
| GetFileVersionInfoExW(A)                   | 不存在时，调用GetFileVersionInfoW(A)。
| GetFileVersionInfoSizeExW(A)               | 不存在时，调用GetFileVersionInfoSizeW(A)。

## ws2_32.dll
| 函数                                       | Fallback
| ----                                       | -----------
| InetPtonW(inet_pton)                       | 不存在时，类似于sscanf手工分析字符串。
| InetNtopW(inet_ntop)                       | 不存在时，类似于sprintf手工生成字符串。
| WSAPoll                                    | 不存在时，调用select。
