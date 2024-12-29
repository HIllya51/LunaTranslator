
DECLARE_API void GetLnkTargetPath(wchar_t *lnkFilePath, wchar_t *path, wchar_t *tgtpath, wchar_t *iconpath, wchar_t *dirpath)
{
    wcscpy(path, L"");
    wcscpy(tgtpath, L"");
    wcscpy(iconpath, L"");
    CoInitialize(NULL);

    CComPtr<IShellLink> shellLink;
    HRESULT hr = CoCreateInstance(CLSID_ShellLink, NULL, CLSCTX_INPROC_SERVER, IID_IShellLink, (LPVOID *)&shellLink);

    if (SUCCEEDED(hr))
    {
        CComPtr<IPersistFile> persistFile;
        auto hr = shellLink.QueryInterface(&persistFile);
        if (SUCCEEDED(hr))
        {
            WCHAR wsz[MAX_PATH];
            StringCchCopy(wsz, MAX_PATH, lnkFilePath);

            hr = persistFile->Load(wsz, STGM_READ);

            if (SUCCEEDED(hr))
            {
                hr = shellLink->Resolve(NULL, SLR_NO_UI);

                if (SUCCEEDED(hr))
                {
                    WIN32_FIND_DATA findData;
                    int x;
                    hr = shellLink->GetIconLocation(iconpath, MAX_PATH, &x);
                    if (FAILED(hr))
                        wcscpy(iconpath, L"");
                    hr = shellLink->GetArguments(tgtpath, MAX_PATH);
                    if (FAILED(hr))
                        wcscpy(tgtpath, L"");
                    hr = shellLink->GetPath(path, MAX_PATH, &findData, SLGP_RAWPATH);

                    if (FAILED(hr))
                        wcscpy(path, L"");
                    hr = shellLink->GetWorkingDirectory(dirpath, MAX_PATH);
                    if (FAILED(hr))
                        wcscpy(path, L"");
                }
            }
        }
    }

    CoUninitialize();
}