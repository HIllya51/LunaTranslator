
DECLARE_API void GetLnkTargetPath(const wchar_t *lnkFilePath, wchar_t *path, wchar_t *tgtpath, wchar_t *iconpath, wchar_t *dirpath)
{
    wcscpy(path, L"");
    wcscpy(tgtpath, L"");
    wcscpy(iconpath, L"");
    wcscpy(dirpath, L"");
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