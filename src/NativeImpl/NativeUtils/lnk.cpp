
DECLARE_API void GetLnkTargetPath(const wchar_t *lnkFilePath, wchar_t *path, wchar_t *tgtpath, wchar_t *iconpath, wchar_t *dirpath)
{
    wcscpy_s(path, MAX_PATH, L"");
    wcscpy_s(tgtpath, MAX_PATH, L"");
    wcscpy_s(iconpath, MAX_PATH, L"");
    wcscpy_s(dirpath, MAX_PATH, L"");
    CO_INIT co;
    CHECK_FAILURE_NORET(co);
    CComPtr<IShellLink> shellLink;
    CHECK_FAILURE_NORET(CoCreateInstance(CLSID_ShellLink, NULL, CLSCTX_INPROC_SERVER, IID_IShellLink, (LPVOID *)&shellLink));

    CComPtr<IPersistFile> persistFile;
    CHECK_FAILURE_NORET(shellLink.QueryInterface(&persistFile));
    WCHAR wsz[MAX_PATH];
    StringCchCopy(wsz, MAX_PATH, lnkFilePath);

    CHECK_FAILURE_NORET(persistFile->Load(lnkFilePath, STGM_READ));

    CHECK_FAILURE_NORET(shellLink->Resolve(NULL, SLR_NO_UI));

    WIN32_FIND_DATA findData;
    int x;
    shellLink->GetIconLocation(iconpath, MAX_PATH, &x);
    shellLink->GetArguments(tgtpath, MAX_PATH);
    shellLink->GetPath(path, MAX_PATH, &findData, SLGP_RAWPATH);
    shellLink->GetWorkingDirectory(dirpath, MAX_PATH);
}

DECLARE_API void CreateShortcut(LPCWSTR shortcutName, LPCWSTR targetPath, LPCWSTR arguments, LPCWSTR iconPath)
{
    CO_INIT co;
    CHECK_FAILURE_NORET(co);
    CComPtr<IShellLink> pShellLink;

    CHECK_FAILURE_NORET(CoCreateInstance(CLSID_ShellLink, NULL, CLSCTX_INPROC_SERVER, IID_IShellLink, (LPVOID *)&pShellLink));

    pShellLink->SetPath(targetPath);
    pShellLink->SetArguments(arguments);
    pShellLink->SetIconLocation(iconPath, 0);
    CComPtr<IPersistFile> pPersistFile;
    CHECK_FAILURE_NORET(pShellLink->QueryInterface(IID_IPersistFile, (LPVOID *)&pPersistFile));

    CComHeapPtr<WCHAR> desktopPath;
    CHECK_FAILURE_NORET(SHGetKnownFolderPath(FOLDERID_Desktop, 0, NULL, &desktopPath));
    std::wstring path = (LPWSTR)desktopPath;
    path += L'\\';
    path += shortcutName;
    int index = 0;
    auto makefilename = [&]()
    {
        return (path + (index ? (L"(" + std::to_wstring(index + 1) + L")") : L"") + L".lnk");
    };
    while (true)
    {
        if (!PathFileExistsW(makefilename().c_str()))
            break;
        index += 1;
    }
    pPersistFile->Save(makefilename().c_str(), TRUE);
}