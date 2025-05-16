#ifndef WINXP
#include <winstring.h>
#include <roapi.h>
#include <inspectable.h>
#include <Windows.Graphics.Capture.Interop.h>
#include <windows.graphics.directx.direct3d11.interop.h>
#include <windows.graphics.directx.direct3d11.h>
#include <windows.graphics.directx.direct3d11.h>
#else
#include "xp.hpp"
#endif

#include "hstring.hpp"
#include "../bmpx.hpp"

using ABI::Windows::Foundation::GetActivationFactory;
using ABI::Windows::Foundation::IClosable;
using ABI::Windows::Foundation::ITypedEventHandler;
using ABI::Windows::Graphics::SizeInt32;
using ABI::Windows::Graphics::Capture::Direct3D11CaptureFramePool;
using ABI::Windows::Graphics::Capture::IDirect3D11CaptureFrame;
using ABI::Windows::Graphics::Capture::IDirect3D11CaptureFramePool;
using ABI::Windows::Graphics::Capture::IDirect3D11CaptureFramePoolStatics;
using ABI::Windows::Graphics::Capture::IGraphicsCaptureItem;
using ABI::Windows::Graphics::Capture::IGraphicsCaptureSession;
using ABI::Windows::Graphics::Capture::IGraphicsCaptureSession2;
using ABI::Windows::Graphics::DirectX::DirectXPixelFormat;
using ABI::Windows::Graphics::DirectX::Direct3D11::IDirect3DDevice;
using ABI::Windows::Graphics::DirectX::Direct3D11::IDirect3DSurface;
using Windows::Graphics::DirectX::Direct3D11::IDirect3DDxgiInterfaceAccess;

_Use_decl_annotations_
    HRESULT
    GetTextureFromSurface(
        IDirect3DSurface *pSurface,
        ID3D11Texture2D **ppTexture)
{
    CComPtr<IDirect3DDxgiInterfaceAccess> spDXGIInterfaceAccess;
    CHECK_FAILURE(pSurface->QueryInterface(&spDXGIInterfaceAccess));
    CHECK_FAILURE(spDXGIInterfaceAccess->GetInterface(IID_PPV_ARGS(ppTexture)));
    return S_OK;
}
struct FrameArrivedCallback : ComImpl<ITypedEventHandler<Direct3D11CaptureFramePool *, IInspectable *>>
{
    CComPtr<ID3D11Texture2D> &texture;
    std::atomic_flag &waitforloadflag;
    bool once = false;
    FrameArrivedCallback(CComPtr<ID3D11Texture2D> &texture, std::atomic_flag &waitforloadflag) : waitforloadflag(waitforloadflag), texture(texture) {}
    HRESULT STDMETHODCALLTYPE Invoke(IDirect3D11CaptureFramePool *frame_pool, IInspectable *args)
    {
        if (once)
            return S_OK;
        CComPtr<IDirect3D11CaptureFrame> frame;
        CHECK_FAILURE(frame_pool->TryGetNextFrame(&frame));
        CComPtr<IDirect3DSurface> surface;
        CHECK_FAILURE(frame->get_Surface(&surface));
        CHECK_FAILURE(GetTextureFromSurface(surface, &texture));
        once = true;
        waitforloadflag.clear();
        return S_OK;
    }
};

void capture_window(HWND window_handle, void (*cb)(byte *, size_t))
{
    // Init COM
    // init_apartment(winrt::apartment_type::multi_threaded);

    // Create Direct 3D Device
    CComPtr<ID3D11Device> d3d_device;

    CHECK_FAILURE_NORET(D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, D3D11_CREATE_DEVICE_BGRA_SUPPORT,
                                          nullptr, 0, D3D11_SDK_VERSION, &d3d_device, nullptr, nullptr));

    CComPtr<IDirect3DDevice> device;
    CComPtr<IDXGIDevice> dxgiDevice;
    CHECK_FAILURE_NORET(d3d_device.QueryInterface(&dxgiDevice));

    {
        CComPtr<IInspectable> inspectable;
        CHECK_FAILURE_NORET(CreateDirect3D11DeviceFromDXGIDevice(dxgiDevice, &inspectable));
        CHECK_FAILURE_NORET(inspectable.QueryInterface(&device));
    }

    CComPtr<ID3D11DeviceContext> d3d_context;
    d3d_device->GetImmediateContext(&d3d_context);

    RECT rect{};
    CHECK_FAILURE_NORET(DwmGetWindowAttribute(window_handle, DWMWA_EXTENDED_FRAME_BOUNDS, &rect, sizeof(RECT)));
    const auto size = SizeInt32{rect.right - rect.left, rect.bottom - rect.top};

    CComPtr<IDirect3D11CaptureFramePoolStatics> framepoolstatics;
    CHECK_FAILURE_NORET(GetActivationFactory(AutoHStringRefX(RuntimeClass_Windows_Graphics_Capture_Direct3D11CaptureFramePool), &framepoolstatics));
    CComPtr<IDirect3D11CaptureFramePool> m_frame_pool;
    CHECK_FAILURE_NORET(framepoolstatics->Create(device, DirectXPixelFormat::DirectXPixelFormat_B8G8R8A8UIntNormalized, 2, size, &m_frame_pool));
    CComPtr<IGraphicsCaptureItemInterop> interop_factory;
    CHECK_FAILURE_NORET(GetActivationFactory(AutoHStringRefX(RuntimeClass_Windows_Graphics_Capture_GraphicsCaptureItem), &interop_factory));
    CComPtr<IGraphicsCaptureItem> capture_item = {nullptr};
    CHECK_FAILURE_NORET(interop_factory->CreateForWindow(window_handle, IID_PPV_ARGS(&capture_item)));

    CComPtr<ID3D11Texture2D> texture;
    CComPtr<IGraphicsCaptureSession> session;
    CHECK_FAILURE_NORET(m_frame_pool->CreateCaptureSession(capture_item, &session));
    CComPtr<IGraphicsCaptureSession2> session2;
    if (SUCCEEDED(session.QueryInterface(&session2)))
        session2->put_IsCursorCaptureEnabled(false);
    EventRegistrationToken token;
    std::atomic_flag waitforloadflag = ATOMIC_FLAG_INIT;
    waitforloadflag.test_and_set();
    CComPtr<FrameArrivedCallback> arrivedCallback = new FrameArrivedCallback{texture, waitforloadflag};
    CHECK_FAILURE_NORET(m_frame_pool->add_FrameArrived(arrivedCallback, &token));

    CHECK_FAILURE_NORET(session->StartCapture());
    MSG message;
    while (waitforloadflag.test_and_set())
    {
        if (PeekMessage(&message, nullptr, 0, 0, PM_REMOVE) > 0)
        {
            DispatchMessage(&message);
        }
    }
    CComPtr<IClosable> closer;
    session.QueryInterface(&closer);
    closer->Close();
    D3D11_TEXTURE2D_DESC captured_texture_desc;
    texture->GetDesc(&captured_texture_desc);
    captured_texture_desc.Usage = D3D11_USAGE_STAGING;
    captured_texture_desc.BindFlags = 0;
    captured_texture_desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
    captured_texture_desc.MiscFlags = 0;
    CComPtr<ID3D11Texture2D> user_texture = nullptr;
    CHECK_FAILURE_NORET(d3d_device->CreateTexture2D(&captured_texture_desc, nullptr, &user_texture));

    d3d_context->CopyResource(user_texture, texture);
    D3D11_MAPPED_SUBRESOURCE resource;
    CHECK_FAILURE_NORET(d3d_context->Map(user_texture, NULL, D3D11_MAP_READ, 0, &resource));

    auto bmp = CreateBMP(captured_texture_desc.Width, captured_texture_desc.Height);

    UINT l_bmp_row_pitch = captured_texture_desc.Width * 4;
    auto sptr = static_cast<BYTE *>(resource.pData);

    UINT l_row_pitch = std::min<UINT>(l_bmp_row_pitch, resource.RowPitch);
    auto ptr = bmp.pixels;
    for (size_t h = 0; h < captured_texture_desc.Height; ++h)
    {
        memcpy_s(ptr, l_bmp_row_pitch, sptr, l_row_pitch);
        sptr += resource.RowPitch;
        ptr += l_bmp_row_pitch;
    }
    d3d_context->Unmap(user_texture, NULL);
    cb(bmp.data.get(), bmp.size);
}
DECLARE_API void winrt_capture_window(HWND hwnd, void (*cb)(byte *, size_t))
{
    // auto hwnd = GetForegroundWindow();// FindWindow(L"Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22", 0);
    auto style_ex = GetWindowLong(hwnd, GWL_EXSTYLE);
    auto style_ex_save = style_ex;
    bool needset = !(((style_ex & WS_EX_APPWINDOW) && !(style_ex & WS_EX_TOOLWINDOW)));
    if (needset)
    {

        style_ex |= WS_EX_APPWINDOW;
        style_ex &= ~WS_EX_TOOLWINDOW;
        SetWindowLong(hwnd, GWL_EXSTYLE, style_ex);
    }
    capture_window(hwnd, cb);
    if (needset)
        SetWindowLong(hwnd, GWL_EXSTYLE, style_ex_save);
}
