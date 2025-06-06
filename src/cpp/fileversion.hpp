
using version_t = std::tuple<DWORD, DWORD, DWORD, DWORD>;
std::optional<version_t> QueryVersion(const std::wstring& exe)
{

    DWORD dwHandle;
    DWORD dwSize = GetFileVersionInfoSizeW(exe.c_str(), &dwHandle);
    if (dwSize == 0)
    {
        return {};
    }

    std::vector<char> versionInfoBuffer(dwSize);
    if (!GetFileVersionInfoW(exe.c_str(), dwHandle, dwSize, versionInfoBuffer.data()))
    {
        return {};
    }

    VS_FIXEDFILEINFO *pFileInfo;
    UINT fileInfoSize;
    if (!VerQueryValueW(versionInfoBuffer.data(), L"\\", reinterpret_cast<LPVOID *>(&pFileInfo), &fileInfoSize))
    {
        return {};
    }

    DWORD ms = pFileInfo->dwFileVersionMS;
    DWORD ls = pFileInfo->dwFileVersionLS;

    WORD majorVersion = HIWORD(ms);
    WORD minorVersion = LOWORD(ms);
    WORD buildNumber = HIWORD(ls);
    WORD revisionNumber = LOWORD(ls);
    return std::make_tuple(majorVersion, minorVersion, buildNumber, revisionNumber);
}