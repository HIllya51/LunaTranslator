from ctypes import (
    c_size_t,
    windll,
    memmove,
    Structure,
    c_uint64,
    cast,
    POINTER,
    sizeof,
    c_char_p,
)
from ctypes.wintypes import LPVOID, DWORD, WORD, LONG, BYTE

ULONGLONG = c_uint64
kernel32 = windll.kernel32
VirtualAlloc = kernel32.VirtualAlloc
VirtualAlloc.argtypes = LPVOID, c_size_t, DWORD, DWORD
VirtualAlloc.restype = LPVOID
VirtualFree = kernel32.VirtualFree
VirtualFree.argtypes = LPVOID, c_size_t, DWORD


class IMAGE_DOS_HEADER(Structure):
    _fields_ = [("_nouse", WORD * 30), ("e_lfanew", LONG)]


class IMAGE_FILE_HEADER(Structure):
    _fields_ = [
        ("Machine", WORD),
        ("NumberOfSections", WORD),
        ("TimeDateStamp", DWORD),
        ("PointerToSymbolTable", DWORD),
        ("NumberOfSymbols", DWORD),
        ("SizeOfOptionalHeader", WORD),
        ("Characteristics", WORD),
    ]


class IMAGE_DATA_DIRECTORY(Structure):
    _fields_ = [
        ("VirtualAddress", DWORD),
        ("Size", DWORD),
    ]


IMAGE_NUMBEROF_DIRECTORY_ENTRIES = 16


class IMAGE_OPTIONAL_HEADER32(Structure):
    _fields_ = [
        ("Magic", WORD),
        ("MajorLinkerVersion", BYTE),
        ("MinorLinkerVersion", BYTE),
        ("SizeOfCode", DWORD),
        ("SizeOfInitializedData", DWORD),
        ("SizeOfUninitializedData", DWORD),
        ("AddressOfEntryPoint", DWORD),
        ("BaseOfCode", DWORD),
        ("BaseOfData", DWORD),
        ("ImageBase", DWORD),
        ("SectionAlignment", DWORD),
        ("FileAlignment", DWORD),
        ("MajorOperatingSystemVersion", WORD),
        ("MinorOperatingSystemVersion", WORD),
        ("MajorImageVersion", WORD),
        ("MinorImageVersion", WORD),
        ("MajorSubsystemVersion", WORD),
        ("MinorSubsystemVersion", WORD),
        ("Win32VersionValue", DWORD),
        ("SizeOfImage", DWORD),
        ("SizeOfHeaders", DWORD),
        ("CheckSum", DWORD),
        ("Subsystem", WORD),
        ("DllCharacteristics", WORD),
        ("SizeOfStackReserve", DWORD),
        ("SizeOfStackCommit", DWORD),
        ("SizeOfHeapReserve", DWORD),
        ("SizeOfHeapCommit", DWORD),
        ("LoaderFlags", DWORD),
        ("NumberOfRvaAndSizes", DWORD),
        ("DataDirectory", IMAGE_DATA_DIRECTORY * IMAGE_NUMBEROF_DIRECTORY_ENTRIES),
    ]


class IMAGE_OPTIONAL_HEADER64(Structure):
    _fields_ = [
        ("Magic", WORD),
        ("MajorLinkerVersion", BYTE),
        ("MinorLinkerVersion", BYTE),
        ("SizeOfCode", DWORD),
        ("SizeOfInitializedData", DWORD),
        ("SizeOfUninitializedData", DWORD),
        ("AddressOfEntryPoint", DWORD),
        ("BaseOfCode", DWORD),
        ("ImageBase", ULONGLONG),
        ("SectionAlignment", DWORD),
        ("FileAlignment", DWORD),
        ("MajorOperatingSystemVersion", WORD),
        ("MinorOperatingSystemVersion", WORD),
        ("MajorImageVersion", WORD),
        ("MinorImageVersion", WORD),
        ("MajorSubsystemVersion", WORD),
        ("MinorSubsystemVersion", WORD),
        ("Win32VersionValue", DWORD),
        ("SizeOfImage", DWORD),
        ("SizeOfHeaders", DWORD),
        ("CheckSum", DWORD),
        ("Subsystem", WORD),
        ("DllCharacteristics", WORD),
        ("SizeOfStackReserve", ULONGLONG),
        ("SizeOfStackCommit", ULONGLONG),
        ("SizeOfHeapReserve", ULONGLONG),
        ("SizeOfHeapCommit", ULONGLONG),
        ("LoaderFlags", DWORD),
        ("NumberOfRvaAndSizes", DWORD),
        ("DataDirectory", IMAGE_DATA_DIRECTORY * IMAGE_NUMBEROF_DIRECTORY_ENTRIES),
    ]


class IMAGE_NT_HEADERS32(Structure):
    _fields_ = [
        ("_nouse", DWORD),
        ("FileHeader", IMAGE_FILE_HEADER),
        ("OptionalHeader", IMAGE_OPTIONAL_HEADER32),
    ]


class IMAGE_NT_HEADERS64(Structure):
    _fields_ = [
        ("_nouse", DWORD),
        ("FileHeader", IMAGE_FILE_HEADER),
        ("OptionalHeader", IMAGE_OPTIONAL_HEADER64),
    ]


IMAGE_SIZEOF_SHORT_NAME = 8


class IMAGE_SECTION_HEADER(Structure):
    _fields_ = [
        ("Name", BYTE * IMAGE_SIZEOF_SHORT_NAME),
        ("VirtualSize", DWORD),
        ("VirtualAddress", DWORD),
        ("SizeOfRawData", DWORD),
        ("PointerToRawData", DWORD),
        ("PointerToRelocations", DWORD),
        ("PointerToLinenumbers", DWORD),
        ("NumberOfRelocations", WORD),
        ("NumberOfLinenumbers", WORD),
        ("Characteristics", DWORD),
    ]


MEM_COMMIT = 0x00001000
MEM_DECOMMIT = 0x00004000
PAGE_READWRITE = 0x04
IMAGE_NT_OPTIONAL_HDR32_MAGIC = 0x10B
IMAGE_NT_OPTIONAL_HDR64_MAGIC = 0x20B
IMAGE_DIRECTORY_ENTRY_IMPORT = 1
IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT = 13


class IMAGE_IMPORT_DESCRIPTOR(Structure):
    _fields_ = [
        ("OriginalFirstThunk", DWORD),
        ("TimeDateStamp", DWORD),
        ("ForwarderChain", DWORD),
        ("Name", DWORD),
        ("FirstThunk", DWORD),
    ]


class IMAGE_DELAYLOAD_DESCRIPTOR(Structure):
    _fields_ = [
        ("Attributes", DWORD),
        ("Name", DWORD),
        ("ModuleHandle", DWORD),
        ("ImportAddressTable", DWORD),
        ("ImportNameTable", DWORD),
        ("BoundImportAddressTable", DWORD),
        ("UnloadInformationTable", DWORD),
        ("TimeDateStamp", DWORD),
    ]


def Rva2Offset(rva, psh, pnt, IMAGE_NT_HEADERS):
    pSeh = psh

    pSeh_start = cast(psh, POINTER(IMAGE_SECTION_HEADER))
    pnt = cast(pnt, POINTER(IMAGE_NT_HEADERS))

    for i in range(pnt.contents.FileHeader.NumberOfSections):
        pSeh_current = pSeh_start[i]
        if (
            rva >= pSeh_current.VirtualAddress
            and rva < pSeh_current.VirtualAddress + pSeh_current.VirtualSize
        ):
            break
    else:
        return -1

    if pSeh_current.VirtualAddress == 0 or pSeh_current.PointerToRawData == 0:
        return -1
    return rva - pSeh_current.VirtualAddress + pSeh_current.PointerToRawData


def importanalysis(fname):
    with open(fname, "rb") as ff:
        bs = ff.read()

    virtualpointer = VirtualAlloc(None, len(bs), MEM_COMMIT, PAGE_READWRITE)
    memmove(virtualpointer, bs, len(bs))

    dos_header = cast(virtualpointer, POINTER(IMAGE_DOS_HEADER)).contents
    ntheaders_addr = virtualpointer + dos_header.e_lfanew

    ntheaders_peek = cast(ntheaders_addr, POINTER(IMAGE_NT_HEADERS32)).contents
    IMAGE_NT_HEADERS_TYPE = None

    if ntheaders_peek.OptionalHeader.Magic == IMAGE_NT_OPTIONAL_HDR32_MAGIC:
        IMAGE_NT_HEADERS_TYPE = IMAGE_NT_HEADERS32
    elif ntheaders_peek.OptionalHeader.Magic == IMAGE_NT_OPTIONAL_HDR64_MAGIC:
        IMAGE_NT_HEADERS_TYPE = IMAGE_NT_HEADERS64
    else:
        VirtualFree(virtualpointer, len(bs), MEM_DECOMMIT)
        return {"imports": [], "delay_imports": []}

    ntheaders = cast(ntheaders_addr, POINTER(IMAGE_NT_HEADERS_TYPE)).contents

    pSech = (
        ntheaders_addr
        + sizeof(DWORD)
        + sizeof(IMAGE_FILE_HEADER)
        + ntheaders.FileHeader.SizeOfOptionalHeader
    )

    imports_collect: "list[tuple[str, int]]" = []
    import_directory_rva = ntheaders.OptionalHeader.DataDirectory[
        IMAGE_DIRECTORY_ENTRY_IMPORT
    ].VirtualAddress

    if import_directory_rva != 0:
        pImportDescriptor = virtualpointer + Rva2Offset(
            import_directory_rva, pSech, ntheaders_addr, IMAGE_NT_HEADERS_TYPE
        )
        if pImportDescriptor != -1:
            pImportDescriptor_data = cast(
                pImportDescriptor, POINTER(IMAGE_IMPORT_DESCRIPTOR)
            ).contents

            current_import_descriptor_ptr = pImportDescriptor
            while pImportDescriptor_data.Name:
                offset = Rva2Offset(
                    pImportDescriptor_data.Name,
                    pSech,
                    ntheaders_addr,
                    IMAGE_NT_HEADERS_TYPE,
                )
                if offset != -1:
                    name = virtualpointer + offset
                    imports_collect.append(
                        (cast(name, c_char_p).value.decode(), offset)
                    )

                current_import_descriptor_ptr += sizeof(IMAGE_IMPORT_DESCRIPTOR)
                pImportDescriptor_data = cast(
                    current_import_descriptor_ptr, POINTER(IMAGE_IMPORT_DESCRIPTOR)
                ).contents

    delay_imports_collect: "list[tuple[str, int]]" = []
    delay_import_directory_rva = ntheaders.OptionalHeader.DataDirectory[
        IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT
    ].VirtualAddress

    if delay_import_directory_rva != 0:
        pDelayImportDescriptor = virtualpointer + Rva2Offset(
            delay_import_directory_rva, pSech, ntheaders_addr, IMAGE_NT_HEADERS_TYPE
        )
        if pDelayImportDescriptor != -1:
            pDelayImportDescriptor_data = cast(
                pDelayImportDescriptor, POINTER(IMAGE_DELAYLOAD_DESCRIPTOR)
            ).contents

            current_delay_import_descriptor_ptr = pDelayImportDescriptor
            while pDelayImportDescriptor_data.Name:
                offset = Rva2Offset(
                    pDelayImportDescriptor_data.Name,
                    pSech,
                    ntheaders_addr,
                    IMAGE_NT_HEADERS_TYPE,
                )
                if offset != -1:
                    name = virtualpointer + offset
                    delay_imports_collect.append(
                        (cast(name, c_char_p).value.decode(), offset)
                    )

                current_delay_import_descriptor_ptr += sizeof(
                    IMAGE_DELAYLOAD_DESCRIPTOR
                )
                pDelayImportDescriptor_data = cast(
                    current_delay_import_descriptor_ptr,
                    POINTER(IMAGE_DELAYLOAD_DESCRIPTOR),
                ).contents

    VirtualFree(virtualpointer, len(bs), MEM_DECOMMIT)
    return {"imports": imports_collect, "delay_imports": delay_imports_collect}


if __name__ == "__main__":
    print(importanalysis(r"D:\GitHub\LunaTranslator\src\files\DLL32\CVUtils.dll"))
    print(importanalysis(r"D:\GitHub\LunaTranslator\src\files\DLL64\NativeUtils.dll"))
