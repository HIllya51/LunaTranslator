// MWebBrowser.cpp --- simple Win32 Web Browser
// Copyright (C) 2019 Katayama Hirofumi MZ <katayama.hirofumi.mz@gmail.com>
// This file is public domain software.

#ifndef MWEB_BROWSER_HPP_
#define MWEB_BROWSER_HPP_ 13 // Version 13

#define INITGUID

class JSObject : public ComImpl<IDispatch>
{
private:
    typedef std::function<void(wchar_t **, int)> functiontype;
    std::map<DISPID, functiontype> funcmap;
    std::map<std::wstring, DISPID> funcnames;

public:
    void bindfunction(const std::wstring &, functiontype);

    // IDispatch
    virtual HRESULT STDMETHODCALLTYPE GetTypeInfoCount(UINT *pctinfo);
    virtual HRESULT STDMETHODCALLTYPE GetTypeInfo(UINT iTInfo, LCID lcid,
                                                  ITypeInfo **ppTInfo);
    virtual HRESULT STDMETHODCALLTYPE GetIDsOfNames(REFIID riid,
                                                    LPOLESTR *rgszNames, UINT cNames, LCID lcid, DISPID *rgDispId);
    virtual HRESULT STDMETHODCALLTYPE Invoke(DISPID dispIdMember, REFIID riid,
                                             LCID lcid, WORD wFlags, DISPPARAMS *pDispParams, VARIANT *pVarResult,
                                             EXCEPINFO *pExcepInfo, UINT *puArgErr);
};

class MWebBrowser : public ComImpl<IDispatch,
                                   IOleClientSite,
                                   IOleInPlaceSite,
                                   IStorage,
                                   IServiceProvider,
                                   IHttpSecurity,
                                   IDocHostUIHandler>
{
public:
    CComPtr<JSObject> jsobj;
    static MWebBrowser *Create(HWND hwndParent);
    HRESULT OnCompleted(DISPPARAMS *args);

    // ---------- IDispatch ----------
    virtual HRESULT STDMETHODCALLTYPE GetTypeInfoCount(__RPC__out UINT *pctinfo) override;
    virtual HRESULT STDMETHODCALLTYPE GetTypeInfo(UINT, LCID, __RPC__deref_out_opt ITypeInfo **) override;
    virtual HRESULT STDMETHODCALLTYPE GetIDsOfNames(__RPC__in REFIID riid, __RPC__in_ecount_full(cNames) LPOLESTR *rgszNames, __RPC__in_range(0, 16384) UINT cNames, LCID lcid, __RPC__out_ecount_full(cNames) DISPID *rgDispId) override;
    virtual HRESULT STDMETHODCALLTYPE Invoke(_In_ DISPID dispIdMember, _In_ REFIID, _In_ LCID, _In_ WORD, _In_ DISPPARAMS *pDispParams, _Out_opt_ VARIANT *pVarResult, _Out_opt_ EXCEPINFO *, _Out_opt_ UINT *) override;

    std::wstring htmlSource;
    IConnectionPoint *callback;
    DWORD eventCookie;

    RECT PixelToHIMETRIC(const RECT &rc);
    HWND GetControlWindow();
    HWND GetIEServerWindow();
    void MoveWindow(const RECT &rc);

    void GoHome();
    void GoBack();
    void GoForward();
    void Stop();
    void StopDownload();
    void Refresh();
    HRESULT Navigate(const WCHAR *url = L"about:blank");
    HRESULT Navigate2(const WCHAR *url, DWORD dwFlags = 0);
    HRESULT SetHtml(const wchar_t *html);
    void Print(BOOL bBang = FALSE);
    void PrintPreview();
    void PageSetup();
    void Destroy();
    BOOL TranslateAccelerator(LPMSG pMsg);
    IWebBrowser2 *GetIWebBrowser2();
    HRESULT GetIHTMLDocument2(IHTMLDocument2 **);
    void AllowInsecure(BOOL bAllow);
    HRESULT Quit();
    HRESULT AddCustomObject(IDispatch *custObj, std::wstring name);
    HRESULT get_Application(IDispatch **ppApplication) const;
    HRESULT get_LocationURL(BSTR *bstrURL) const;
    HRESULT put_Silent(VARIANT_BOOL bSilent);
    BOOL is_busy() const;
    HRESULT ZoomUp();
    HRESULT ZoomDown();
    HRESULT Zoom100();
    HRESULT ZoomPercents(LONG percents);

    // IOleWindow interface
    STDMETHODIMP GetWindow(HWND *phwnd);
    STDMETHODIMP ContextSensitiveHelp(BOOL fEnterMode);

    // IOleInPlaceSite interface
    STDMETHODIMP CanInPlaceActivate();
    STDMETHODIMP OnInPlaceActivate();
    STDMETHODIMP OnUIActivate();
    STDMETHODIMP GetWindowContext(
        IOleInPlaceFrame **ppFrame,
        IOleInPlaceUIWindow **ppDoc,
        LPRECT lprcPosRect,
        LPRECT lprcClipRect,
        LPOLEINPLACEFRAMEINFO lpFrameInfo);
    STDMETHODIMP Scroll(SIZE scrollExtant);
    STDMETHODIMP OnUIDeactivate(BOOL fUndoable);
    STDMETHODIMP OnInPlaceDeactivate();
    STDMETHODIMP DiscardUndoState();
    STDMETHODIMP DeactivateAndUndo();
    STDMETHODIMP OnPosRectChange(LPCRECT lprcPosRect);

    // IOleClientSite interface
    STDMETHODIMP SaveObject();
    STDMETHODIMP GetMoniker(
        DWORD dwAssign,
        DWORD dwWhichMoniker,
        IMoniker **ppmk);
    STDMETHODIMP GetContainer(IOleContainer **ppContainer);
    STDMETHODIMP ShowObject();
    STDMETHODIMP OnShowWindow(BOOL fShow);
    STDMETHODIMP RequestNewObjectLayout();

    // IStorage interface
    STDMETHODIMP CreateStream(
        const OLECHAR *pwcsName,
        DWORD grfMode,
        DWORD reserved1,
        DWORD reserved2,
        IStream **ppstm);
    STDMETHODIMP OpenStream(
        const OLECHAR *pwcsName,
        void *reserved1,
        DWORD grfMode,
        DWORD reserved2,
        IStream **ppstm);
    STDMETHODIMP CreateStorage(
        const OLECHAR *pwcsName,
        DWORD grfMode,
        DWORD reserved1,
        DWORD reserved2,
        IStorage **ppstg);
    STDMETHODIMP OpenStorage(
        const OLECHAR *pwcsName,
        IStorage *pstgPriority,
        DWORD grfMode,
        SNB snbExclude,
        DWORD reserved,
        IStorage **ppstg);
    STDMETHODIMP CopyTo(
        DWORD ciidExclude,
        const IID *rgiidExclude,
        SNB snbExclude,
        IStorage *pstgDest);
    STDMETHODIMP MoveElementTo(
        const OLECHAR *pwcsName,
        IStorage *pstgDest,
        const OLECHAR *pwcsNewName,
        DWORD grfFlags);
    STDMETHODIMP Commit(DWORD grfCommitFlags);
    STDMETHODIMP Revert();
    STDMETHODIMP EnumElements(
        DWORD reserved1,
        void *reserved2,
        DWORD reserved3,
        IEnumSTATSTG **ppenum);
    STDMETHODIMP DestroyElement(const OLECHAR *pwcsName);
    STDMETHODIMP RenameElement(
        const OLECHAR *pwcsOldName,
        const OLECHAR *pwcsNewName);
    STDMETHODIMP SetElementTimes(
        const OLECHAR *pwcsName,
        const FILETIME *pctime,
        const FILETIME *patime,
        const FILETIME *pmtime);
    STDMETHODIMP SetClass(REFCLSID clsid);
    STDMETHODIMP SetStateBits(DWORD grfStateBits, DWORD grfMask);
    STDMETHODIMP Stat(STATSTG *pstatstg, DWORD grfStatFlag);

    // IServiceProvider interface
    STDMETHODIMP QueryService(
        REFGUID guidService,
        REFIID riid,
        void **ppvObject);

    // IWindowForBindingUI interface
    STDMETHODIMP GetWindow(REFGUID rguidReason, HWND *phwnd);

    // IHttpSecurity interface
    STDMETHODIMP OnSecurityProblem(DWORD dwProblem);

    // IDocHostUIHandler interface
    STDMETHODIMP ShowContextMenu(
        DWORD dwID,
        POINT *ppt,
        IUnknown *pcmdtReserved,
        IDispatch *pdispReserved);
    STDMETHODIMP GetHostInfo(DOCHOSTUIINFO *pInfo);
    STDMETHODIMP ShowUI(
        DWORD dwID,
        IOleInPlaceActiveObject *pActiveObject,
        IOleCommandTarget *pCommandTarget,
        IOleInPlaceFrame *pFrame,
        IOleInPlaceUIWindow *pDoc);
    STDMETHODIMP HideUI();
    STDMETHODIMP UpdateUI();
    STDMETHODIMP EnableModeless(BOOL fEnable);
    STDMETHODIMP OnDocWindowActivate(BOOL fActivate);
    STDMETHODIMP OnFrameWindowActivate(BOOL fActivate);
    STDMETHODIMP ResizeBorder(
        LPCRECT prcBorder,
        IOleInPlaceUIWindow *pUIWindow,
        BOOL fRameWindow);
    STDMETHODIMP TranslateAccelerator(
        LPMSG lpMsg,
        const GUID *pguidCmdGroup,
        DWORD nCmdID);
    STDMETHODIMP GetOptionKeyPath(LPOLESTR *pchKey, DWORD dw);
    STDMETHODIMP GetDropTarget(
        IDropTarget *pDropTarget,
        IDropTarget **ppDropTarget);
    STDMETHODIMP GetExternal(IDispatch **ppDispatch);
    STDMETHODIMP TranslateUrl(
        DWORD dwTranslate,
        OLECHAR *pchURLIn,
        OLECHAR **ppchURLOut);
    STDMETHODIMP FilterDataObject(IDataObject *pDO, IDataObject **ppDORet);

protected:
    HWND m_hwndParent;
    HWND m_hwndCtrl;
    HWND m_hwndIEServer;
    CComPtr<IWebBrowser2> m_web_browser2;
    CComPtr<IOleObject> m_ole_object;
    CComPtr<IOleInPlaceObject> m_ole_inplace_object;
    CComPtr<IDocHostUIHandler> m_pDocHostUIHandler;
    RECT m_rc;
    HRESULT m_hr;
    BOOL m_bAllowInsecure;
    LONG m_nZoomPercents;

    MWebBrowser(HWND hwndParent);

    HRESULT CreateBrowser(HWND hwndParent);
    BOOL IsCreated() const;

private:
    MWebBrowser(const MWebBrowser &);
    MWebBrowser &operator=(const MWebBrowser &);
};

#endif // ndef MWEB_BROWSER_HPP_
