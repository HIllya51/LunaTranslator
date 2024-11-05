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


class IMAGE_IMPORT_DESCRIPTOR(Structure):
    _fields_ = [
        ("OriginalFirstThunk", DWORD),
        ("TimeDateStamp", DWORD),
        ("ForwarderChain", DWORD),
        ("Name", DWORD),
        ("FirstThunk", DWORD),
    ]


def Rva2Offset(rva, psh, pnt, IMAGE_NT_HEADERS):
    pSeh = psh
    psh = cast(psh, POINTER(IMAGE_SECTION_HEADER))
    pnt = cast(pnt, POINTER(IMAGE_NT_HEADERS))
    for i in range(pnt.contents.FileHeader.NumberOfSections):
        pSeh1 = cast(pSeh, POINTER(IMAGE_SECTION_HEADER)).contents
        if (
            rva >= pSeh1.VirtualAddress
            and rva < pSeh1.VirtualAddress + pSeh1.VirtualSize
        ):
            break
        pSeh += sizeof(IMAGE_SECTION_HEADER)
    pSeh = cast(pSeh, POINTER(IMAGE_SECTION_HEADER)).contents
    if pSeh.VirtualAddress == 0 or pSeh.PointerToRawData == 0:
        return -1
    return rva - pSeh.VirtualAddress + pSeh.PointerToRawData


def importanalysis(fname):
    with open(fname, "rb") as ff:
        bs = ff.read()

    virtualpointer = VirtualAlloc(None, len(bs), MEM_COMMIT, PAGE_READWRITE)
    memmove(virtualpointer, bs, len(bs))
    ntheaders_addr = (
        virtualpointer
        + cast(virtualpointer, POINTER(IMAGE_DOS_HEADER)).contents.e_lfanew
    )
    ntheaders = cast(ntheaders_addr, POINTER(IMAGE_NT_HEADERS32)).contents
    IMAGE_NT_HEADERS = IMAGE_NT_HEADERS32
    magic = ntheaders.OptionalHeader.Magic
    if magic != IMAGE_NT_OPTIONAL_HDR32_MAGIC:
        ntheaders = cast(ntheaders_addr, POINTER(IMAGE_NT_HEADERS64)).contents
        IMAGE_NT_HEADERS = IMAGE_NT_HEADERS64
        magic = ntheaders.OptionalHeader.Magic
        if magic != IMAGE_NT_OPTIONAL_HDR64_MAGIC:
            # 无效的文件
            return []
    pSech = (
        ntheaders_addr
        + sizeof(DWORD)
        + sizeof(IMAGE_FILE_HEADER)
        + ntheaders.FileHeader.SizeOfOptionalHeader
    )

    pImportDescriptor = virtualpointer + Rva2Offset(
        ntheaders.OptionalHeader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_IMPORT
        ].VirtualAddress,
        pSech,
        ntheaders_addr,
        IMAGE_NT_HEADERS,
    )
    pImportDescriptor_data = cast(
        pImportDescriptor, POINTER(IMAGE_IMPORT_DESCRIPTOR)
    ).contents
    collect = []
    while pImportDescriptor_data.Name:
        offset = Rva2Offset(
            pImportDescriptor_data.Name, pSech, ntheaders_addr, IMAGE_NT_HEADERS
        )
        if offset == -1:
            # python3.dll，无导入
            return []
        name = virtualpointer + offset
        collect.append((cast(name, c_char_p).value.decode(), offset))
        pImportDescriptor += sizeof(IMAGE_IMPORT_DESCRIPTOR)
        pImportDescriptor_data = cast(
            pImportDescriptor, POINTER(IMAGE_IMPORT_DESCRIPTOR)
        ).contents
    VirtualFree(virtualpointer, len(bs), MEM_DECOMMIT)
    return collect
