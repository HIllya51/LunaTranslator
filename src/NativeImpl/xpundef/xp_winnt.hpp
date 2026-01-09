
typedef struct _IMAGE_DELAYLOAD_DESCRIPTOR
{
    union
    {
        DWORD AllAttributes;
        struct
        {
            DWORD RvaBased : 1; // Delay load version 2
            DWORD ReservedAttributes : 31;
        } DUMMYSTRUCTNAME;
    } Attributes;

    DWORD DllNameRVA;                 // RVA to the name of the target library (NULL-terminate ASCII string)
    DWORD ModuleHandleRVA;            // RVA to the HMODULE caching location (PHMODULE)
    DWORD ImportAddressTableRVA;      // RVA to the start of the IAT (PIMAGE_THUNK_DATA)
    DWORD ImportNameTableRVA;         // RVA to the start of the name table (PIMAGE_THUNK_DATA::AddressOfData)
    DWORD BoundImportAddressTableRVA; // RVA to an optional bound IAT
    DWORD UnloadInformationTableRVA;  // RVA to an optional unload info table
    DWORD TimeDateStamp;              // 0 if not bound,
                                      // Otherwise, date/time of the target DLL

} IMAGE_DELAYLOAD_DESCRIPTOR, *PIMAGE_DELAYLOAD_DESCRIPTOR;

typedef const IMAGE_DELAYLOAD_DESCRIPTOR *PCIMAGE_DELAYLOAD_DESCRIPTOR;