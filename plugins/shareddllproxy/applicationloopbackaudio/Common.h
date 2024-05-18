#pragma once

#include <mfidl.h>
#include <mfapi.h>
#include <mfobjects.h>

#ifndef METHODASYNCCALLBACK
#define METHODASYNCCALLBACK(Parent, AsyncCallback, pfnCallback) \
class Callback##AsyncCallback :\
    public IMFAsyncCallback \
{ \
public: \
    Callback##AsyncCallback() : \
        _parent(((Parent*)((BYTE*)this - offsetof(Parent, m_x##AsyncCallback)))), \
        _dwQueueID( MFASYNC_CALLBACK_QUEUE_MULTITHREADED ) \
    { \
    } \
\
    STDMETHOD_( ULONG, AddRef )() \
    { \
        return _parent->AddRef(); \
    } \
    STDMETHOD_( ULONG, Release )() \
    { \
        return _parent->Release(); \
    } \
    STDMETHOD( QueryInterface )( REFIID riid, void **ppvObject ) \
    { \
        if (riid == IID_IMFAsyncCallback || riid == IID_IUnknown) \
        { \
            (*ppvObject) = this; \
            AddRef(); \
            return S_OK; \
        } \
        *ppvObject = NULL; \
        return E_NOINTERFACE; \
    } \
    STDMETHOD( GetParameters )( \
        /* [out] */ __RPC__out DWORD *pdwFlags, \
        /* [out] */ __RPC__out DWORD *pdwQueue) \
    { \
        *pdwFlags = 0; \
        *pdwQueue = _dwQueueID; \
        return S_OK; \
    } \
    STDMETHOD( Invoke )( /* [out] */ __RPC__out IMFAsyncResult * pResult ) \
    { \
        _parent->pfnCallback( pResult ); \
        return S_OK; \
    } \
    void SetQueueID( DWORD dwQueueID ) { _dwQueueID = dwQueueID; } \
\
protected: \
    Parent* _parent; \
    DWORD   _dwQueueID; \
           \
} m_x##AsyncCallback;
#endif
