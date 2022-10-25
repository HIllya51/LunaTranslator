// Defines an event handler for focus changed events and starts
// listening to them.
#include <windows.h>
#include <stdio.h>
#include <UIAutomation.h>

class EventHandler :
    public IUIAutomationFocusChangedEventHandler
{
private:
    LONG _refCount;

public:
    int _eventCount;

    //Constructor.
    EventHandler() : _refCount(1), _eventCount(0)
    {
    }

    //IUnknown methods.
    ULONG STDMETHODCALLTYPE AddRef()
    {
        ULONG ret = InterlockedIncrement(&_refCount);
        return ret;
    }

    ULONG STDMETHODCALLTYPE Release()
    {
        ULONG ret = InterlockedDecrement(&_refCount);
        if (ret == 0)
        {
            delete this;
            return 0;
        }
        return ret;
    }

    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void** ppInterface)
    {
        if (riid == __uuidof(IUnknown))
            *ppInterface = static_cast<IUIAutomationFocusChangedEventHandler*>(this);
        else if (riid == __uuidof(IUIAutomationFocusChangedEventHandler))
            *ppInterface = static_cast<IUIAutomationFocusChangedEventHandler*>(this);
        else
        {
            *ppInterface = NULL;
            return E_NOINTERFACE;
        }
        this->AddRef();
        return S_OK;
    }

    // IUIAutomationFocusChangedEventHandler methods.
    HRESULT STDMETHODCALLTYPE HandleFocusChangedEvent(IUIAutomationElement* pSender)
    {
        _eventCount++;
        wprintf(L">> FocusChangedEvent Received! (count: %d)\n", _eventCount);
        return S_OK;
    }
};

int main(int argc, char* argv[])
{
    HRESULT hr;
    int ret = 0;
    EventHandler* pEHTemp = NULL;

    CoInitializeEx(NULL, COINIT_MULTITHREADED);
    IUIAutomation* pAutomation = NULL;
    hr = CoCreateInstance(__uuidof(CUIAutomation), NULL, CLSCTX_INPROC_SERVER, __uuidof(IUIAutomation), (void**)&pAutomation);
    if (FAILED(hr) || pAutomation == NULL)
    {
        ret = 1;
        goto cleanup;
    }

    pEHTemp = new EventHandler();
    if (pEHTemp == NULL)
    {
        ret = 1;
        goto cleanup;
    }

    wprintf(L"-Adding Event Handlers.\n");
    hr = pAutomation->AddFocusChangedEventHandler(NULL, (IUIAutomationFocusChangedEventHandler*)pEHTemp);
    if (FAILED(hr))
    {
        ret = 1;
        goto cleanup;
    }

    wprintf(L"-Press any key to remove event handler and exit\n");
    getchar();

    wprintf(L"-Removing Event Handlers.\n");
    hr = pAutomation->RemoveFocusChangedEventHandler((IUIAutomationFocusChangedEventHandler*)pEHTemp);
    if (FAILED(hr))
    {
        ret = 1;
        goto cleanup;
    }

    // Release resources and terminate.
cleanup:
    if (pEHTemp != NULL)
        pEHTemp->Release();

    if (pAutomation != NULL)
        pAutomation->Release();

    CoUninitialize();
    return ret;
}