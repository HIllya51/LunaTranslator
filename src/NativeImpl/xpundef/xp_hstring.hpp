
#ifndef __hstring_h__
#define __hstring_h__

typedef struct HSTRING__
{
    int unused;
} HSTRING__;

// Declare the HSTRING handle for C/C++
typedef __RPC_unique_pointer HSTRING__ *HSTRING;

// Declare the HSTRING_HEADER
typedef struct HSTRING_HEADER
{
    union
    {
        PVOID Reserved1;
#if defined(_WIN64)
        char Reserved2[24];
#else
        char Reserved2[20];
#endif
    } Reserved;
} HSTRING_HEADER;

STDAPI
WindowsCreateString(
    _In_reads_opt_(length) PCNZWCH sourceString,
    UINT32 length,
    _Outptr_result_maybenull_ _Result_nullonfailure_ HSTRING *string);
STDAPI
WindowsCreateStringReference(
    _In_reads_opt_(length + 1) PCWSTR sourceString,
    UINT32 length,
    _Out_ HSTRING_HEADER *hstringHeader,
    _Outptr_result_maybenull_ _Result_nullonfailure_ HSTRING *string);
STDAPI
WindowsDeleteString(
    _In_opt_ HSTRING string);

STDAPI_(PCWSTR)
WindowsGetStringRawBuffer(
    _In_opt_ HSTRING string,
    _Out_opt_ UINT32 *length);
#endif