
using ABI::Windows::Foundation::IAsyncOperationCompletedHandler;

template <class T, class IT>
struct awaithelper_CompleteCallback : ComImpl<IAsyncOperationCompletedHandler<T *>>
{
    CoAsyncTaskWaiter &event;
    HRESULT &hrCallback;
    IT **ppResult;
    ABI::Windows::Foundation::IAsyncOperation<T *> *pAsync;
    awaithelper_CompleteCallback(ABI::Windows::Foundation::IAsyncOperation<T *> *pAsync, CoAsyncTaskWaiter &event, HRESULT &hrCallback, IT **ppResult) : pAsync(pAsync), event(event), hrCallback(hrCallback), ppResult(ppResult) {}
    HRESULT STDMETHODCALLTYPE Invoke(ABI::Windows::Foundation::IAsyncOperation<T *> *asyncInfo, ABI::Windows::Foundation::AsyncStatus status)
    {
        hrCallback = (status == ABI::Windows::Foundation::AsyncStatus::Completed) ? pAsync->GetResults(ppResult) : E_FAIL;
        event.Set();
        return hrCallback;
    }
};
template <class T, class IT>
HRESULT await(ABI::Windows::Foundation::IAsyncOperation<T *> *pAsync, IT **ppResult)
{
    CoAsyncTaskWaiter co;
    HRESULT hrCallback = E_FAIL;
    auto hr = pAsync->put_Completed(new awaithelper_CompleteCallback<T, IT>(pAsync, co, hrCallback, ppResult));
    if (FAILED(hr))
        return hr;
    co.Wait();
    return hrCallback;
}