#!/usr/bin/env python3
"""
Dump the Fragments Blue decoded glyph bitmap cache from a RUNNING PCSX2 process.

The font FC.BIN is decoded at runtime into a 24x24 2bpp bitmap cache.  The cache
base pointer lives in PS2 main RAM at 0x218620 (= [gp-0x7ed0], set in 0x1b7e80).
The cache is 0x7B800 bytes = 3520 glyphs * 144 bytes/glyph (24*24*2bpp).

PCSX2 exports `EEmem` (a pointer to its EEVM_MemoryAllocMess struct; Main RAM is
the first field, so the pointer value IS the PS2 main-RAM host base).  LunaHook
uses the same trick (PCSX2.cpp:265).  We resolve EEmem from the remote process's
export table, ReadProcessMemory the pointer, then read the cache.

Usage:
  1. Boot Fragments Blue in PCSX2 and reach the title/main menu (font must load).
  2. python dump_glyphcache.py
  3. Writes ../glyphcache.bin (506880 bytes) and prints the resolved addresses.

If it fails, fall back to PCSX2's debugger: jump to 0x218620, read the u32
pointer, jump there, "Save dump" 0x7B800 bytes -> glyphcache.bin.
"""
import ctypes, ctypes.wintypes as w, struct, sys

PROCESS_VM_READ = 0x10
PROCESS_QUERY_INFORMATION = 0x400

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)

# --- find PCSX2 process ---
class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", w.DWORD), ("cntUsage", w.DWORD), ("th32ProcessID", w.DWORD),
                ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
                ("th32ModuleID", w.DWORD), ("cntThreads", w.DWORD),
                ("th32ParentProcessID", w.DWORD), ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", w.DWORD), ("szExeFile", ctypes.c_wchar * 260)]

def find_pcsx2():
    snap = k32.CreateToolhelp32Snapshot(0x2, 0)  # TH32CS_SNAPPROCESS
    e = PROCESSENTRY32W(); e.dwSize = ctypes.sizeof(e)
    pid = None
    if k32.Process32FirstW(snap, ctypes.byref(e)):
        while True:
            name = e.szExeFile.lower()
            if "pcsx2" in name:
                pid = e.th32ProcessID; print("[*] Found %s pid=%d" % (e.szExeFile, pid)); break
            if not k32.Process32NextW(snap, ctypes.byref(e)): break
    k32.CloseHandle(snap)
    return pid

def read_mem(h, addr, n):
    buf = (ctypes.c_ubyte * n)()
    read = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, n, ctypes.byref(read))
    if not ok or read.value != n:
        return None
    return bytes(buf[:n])

def main_module_base(h):
    """Return base address of the main exe (first module)."""
    arr = (w.HMODULE * 1024)()
    needed = w.DWORD()
    psapi.EnumProcessModulesEx(h, arr, ctypes.sizeof(arr), ctypes.byref(needed), 3)
    return arr[0]  # first = main module

def export_rva(h, base, func_name):
    """Resolve an exported symbol name -> RVA in a remote PE module."""
    # DOS header
    hdr = read_mem(h, base, 0x400)
    if not hdr: return None
    e_lfanew = struct.unpack_from("<I", hdr, 0x3C)[0]
    pe = read_mem(h, base + e_lfanew, 0x108 + 0x200)
    if not pe or pe[:4] != b"PE\x00\x00": return None
    # PE sig(4) + FileHeader(20) -> OptionalHeader magic
    opt_off = 4 + 20
    magic = struct.unpack_from("<H", pe, opt_off)[0]
    # DataDirectory starts at offset depending on PE32 (0x60) vs PE32+ (0x70) from opt
    dd_off = opt_off + (0x60 if magic == 0x10b else 0x70)
    exp_rva = struct.unpack_from("<I", pe, dd_off)[0]
    exp_size = struct.unpack_from("<I", pe, dd_off + 4)[0]
    if not exp_rva: return None
    edt = read_mem(h, base + exp_rva, 40)
    if not edt: return None
    nNames = struct.unpack_from("<I", edt, 0x18)[0]
    addrNames = struct.unpack_from("<I", edt, 0x20)[0]
    addrOrd = struct.unpack_from("<I", edt, 0x24)[0]
    addrFuncs = struct.unpack_from("<I", edt, 0x1C)[0]
    # read name pointer array
    names = read_mem(h, base + addrNames, 4 * nNames)
    ords = read_mem(h, base + addrOrd, 2 * nNames)
    funcs = read_mem(h, base + addrFuncs, 4 * nNames)
    if not (names and ords and funcs): return None
    fnb = func_name.encode()
    for i in range(nNames):
        nrva = struct.unpack_from("<I", names, i * 4)[0]
        nm = read_mem(h, base + nrva, len(fnb) + 1)
        if nm and nm.split(b"\x00")[0] == fnb:
            o = struct.unpack_from("<H", ords, i * 2)[0]
            return struct.unpack_from("<I", funcs, o * 4)[0]
    return None

CTX_PTR = 0x218620          # [gp-0x7ed0]: holds cache base (PS2 addr)
CACHE_SIZE = 0x7B800        # 506880 = 3520 * 144

def main():
    pid = find_pcsx2()
    if not pid:
        print("[!] PCSX2 process not found. Boot the game first."); sys.exit(1)
    h = k32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not h:
        print("[!] OpenProcess failed: %d" % ctypes.get_last_error()); sys.exit(1)
    base = main_module_base(h)
    print("[*] Main module base = 0x%X" % base)
    rva = export_rva(h, base, "EEmem")
    if rva is None:
        print("[!] EEmem export not found in main module."); sys.exit(1)
    print("[*] EEmem RVA = 0x%X" % rva)
    ptr = read_mem(h, base + rva, 8)
    if not ptr:
        print("[!] Cannot read EEmem pointer."); sys.exit(1)
    eeMem = struct.unpack("<Q", ptr)[0]
    print("[*] eeMem (PS2 main RAM host base) = 0x%X" % eeMem)
    # read cache pointer at PS2 addr 0x218620
    cptr_b = read_mem(h, eeMem + CTX_PTR, 4)
    if not cptr_b:
        print("[!] Cannot read [0x218620]."); sys.exit(1)
    cache_ps2 = struct.unpack("<I", cptr_b)[0]
    print("[*] cache base (PS2 addr) = 0x%08X" % cache_ps2)
    if cache_ps2 == 0 or cache_ps2 >= 0x2000000:
        print("[!] Cache pointer looks invalid (0). Reach the main menu so the font loads, then retry."); sys.exit(1)
    data = read_mem(h, eeMem + cache_ps2, CACHE_SIZE)
    if not data:
        print("[!] Cannot read cache memory."); sys.exit(1)
    out = "../glyphcache.bin"
    open(out, "wb").write(data)
    print("[+] Wrote %d bytes to %s" % (len(data), out))
    print("[+] Now run: python render_glyphs.py   (then gen_glyphmap.py)")
    k32.CloseHandle(h)

if __name__ == "__main__":
    main()
