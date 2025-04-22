

DECLARE_API bool QueryVersion(const wchar_t *exe, WORD *_1, WORD *_2, WORD *_3, WORD *_4)
{

    DWORD dwHandle;
    DWORD dwSize = GetFileVersionInfoSizeW(exe, &dwHandle);
    if (dwSize == 0)
    {
        return false;
    }

    std::vector<char> versionInfoBuffer(dwSize);
    if (!GetFileVersionInfoW(exe, dwHandle, dwSize, versionInfoBuffer.data()))
    {
        return false;
    }

    VS_FIXEDFILEINFO *pFileInfo;
    UINT fileInfoSize;
    if (!VerQueryValueW(versionInfoBuffer.data(), L"\\", reinterpret_cast<LPVOID *>(&pFileInfo), &fileInfoSize))
    {
        return false;
    }

    DWORD ms = pFileInfo->dwFileVersionMS;
    DWORD ls = pFileInfo->dwFileVersionLS;

    WORD majorVersion = HIWORD(ms);
    WORD minorVersion = LOWORD(ms);
    WORD buildNumber = HIWORD(ls);
    WORD revisionNumber = LOWORD(ls);
    *_1 = majorVersion;
    *_2 = minorVersion;
    *_3 = buildNumber;
    *_4 = revisionNumber;
    return true;
}