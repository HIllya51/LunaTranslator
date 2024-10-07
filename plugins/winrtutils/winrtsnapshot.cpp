#include "define.h"
#include <dxgi.h>
#include <inspectable.h>
#include <dxgi1_2.h>
#include <d3d11.h>
#include <winrt/Windows.System.h>
#include <winrt/Windows.Foundation.h>
#include <winrt/Windows.Foundation.Collections.h>
#include <winrt/Windows.Graphics.Capture.h>
#include <Windows.Graphics.Capture.Interop.h>
#include <windows.graphics.directx.direct3d11.interop.h>
#include <winrt/Windows.Foundation.Metadata.h>
#include <winrt/Windows.Graphics.DirectX.h>
#include <winrt/Windows.Graphics.DirectX.Direct3d11.h>
#include <winrt/Windows.Graphics.Imaging.h>
#include <winrt/Windows.Security.Authorization.AppCapabilityAccess.h>
#include <winrt/Windows.Storage.h>
#include <winrt/Windows.Storage.Pickers.h>
#include <winrt/Windows.Storage.Streams.h>
#include <roerrorapi.h>
#include <gdiplus.h>
// #include "ImageFormatConversion.hpp"

#pragma comment(lib, "windowsapp.lib")
#pragma comment(lib, "DXGI.lib")
#pragma comment(lib, "gdiplus.lib")
#pragma comment(lib, "d3d11.lib")
#pragma comment(lib, "Windowscodecs.lib")
int GetEncoderClsid(const WCHAR *format, CLSID *pClsid)
{
    UINT num = 0;  // number of image encoders
    UINT size = 0; // size of the image encoder array in bytes

    Gdiplus::ImageCodecInfo *pImageCodecInfo = NULL;

    Gdiplus::GetImageEncodersSize(&num, &size);
    if (size == 0)
        return -1; // Failure

    pImageCodecInfo = (Gdiplus::ImageCodecInfo *)(malloc(size));
    if (pImageCodecInfo == NULL)
        return -1; // Failure

    GetImageEncoders(num, size, pImageCodecInfo);

    for (UINT j = 0; j < num; ++j)
    {
        if (wcscmp(pImageCodecInfo[j].MimeType, format) == 0)
        {
            *pClsid = pImageCodecInfo[j].Clsid;
            free(pImageCodecInfo);
            return j; // Success
        }
    }

    free(pImageCodecInfo);
    return -1; // Failure
}
void capture_window(HWND window_handle, void (*cb)(byte *, size_t))
{
    HMODULE hModule = GetModuleHandle(TEXT("d3d11.dll"));
    if (!hModule)
        hModule = LoadLibrary(TEXT("d3d11.dll"));
    HRESULT typedef(_stdcall * CreateDirect3D11DeviceFromDXGIDevice_t)(
        _In_ IDXGIDevice * dxgiDevice,
        _COM_Outptr_ IInspectable * *graphicsDevice);
    CreateDirect3D11DeviceFromDXGIDevice_t CreateDirect3D11DeviceFromDXGIDevice = reinterpret_cast<CreateDirect3D11DeviceFromDXGIDevice_t>(
        GetProcAddress(hModule, "CreateDirect3D11DeviceFromDXGIDevice"));
    if (CreateDirect3D11DeviceFromDXGIDevice == NULL)
        return;
    // Init COM
    // init_apartment(winrt::apartment_type::multi_threaded);

    // Create Direct 3D Device
    winrt::com_ptr<ID3D11Device> d3d_device;

    winrt::check_hresult(D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, D3D11_CREATE_DEVICE_BGRA_SUPPORT,
                                           nullptr, 0, D3D11_SDK_VERSION, d3d_device.put(), nullptr, nullptr));

    winrt::Windows::Graphics::DirectX::Direct3D11::IDirect3DDevice device;
    const auto dxgiDevice = d3d_device.as<IDXGIDevice>();
    {
        winrt::com_ptr<IInspectable> inspectable;
        winrt::check_hresult(CreateDirect3D11DeviceFromDXGIDevice(dxgiDevice.get(), inspectable.put()));
        device = inspectable.as<winrt::Windows::Graphics::DirectX::Direct3D11::IDirect3DDevice>();
    }

    auto idxgi_device2 = dxgiDevice.as<IDXGIDevice2>();
    winrt::com_ptr<IDXGIAdapter> adapter;
    winrt::check_hresult(idxgi_device2->GetParent(winrt::guid_of<IDXGIAdapter>(), adapter.put_void()));
    winrt::com_ptr<IDXGIFactory2> factory;
    winrt::check_hresult(adapter->GetParent(winrt::guid_of<IDXGIFactory2>(), factory.put_void()));

    winrt::com_ptr<ID3D11DeviceContext> d3d_context;
    d3d_device->GetImmediateContext(d3d_context.put());

    RECT rect{};
    DwmGetWindowAttribute(window_handle, DWMWA_EXTENDED_FRAME_BOUNDS, &rect, sizeof(RECT));
    const auto size = winrt::Windows::Graphics::SizeInt32{rect.right - rect.left, rect.bottom - rect.top};

    winrt::Windows::Graphics::Capture::Direct3D11CaptureFramePool m_frame_pool =
        winrt::Windows::Graphics::Capture::Direct3D11CaptureFramePool::Create(
            device,
            winrt::Windows::Graphics::DirectX::DirectXPixelFormat::B8G8R8A8UIntNormalized,
            2,
            size);

    const auto activation_factory = winrt::get_activation_factory<
        winrt::Windows::Graphics::Capture::GraphicsCaptureItem>();
    auto interop_factory = activation_factory.as<IGraphicsCaptureItemInterop>();
    winrt::Windows::Graphics::Capture::GraphicsCaptureItem capture_item = {nullptr};
    interop_factory->CreateForWindow(window_handle, winrt::guid_of<ABI::Windows::Graphics::Capture::IGraphicsCaptureItem>(),
                                     winrt::put_abi(capture_item));

    auto is_frame_arrived = false;
    winrt::com_ptr<ID3D11Texture2D> texture;
    const auto session = m_frame_pool.CreateCaptureSession(capture_item);
    session.IsCursorCaptureEnabled(false);
    m_frame_pool.FrameArrived([&](auto &frame_pool, auto &)
                              {
            if (is_frame_arrived)
            {
                return;
            }
            auto frame = frame_pool.TryGetNextFrame();

            struct __declspec(uuid("A9B3D012-3DF2-4EE3-B8D1-8695F457D3C1"))
                IDirect3DDxgiInterfaceAccess : ::IUnknown
            {
                virtual HRESULT __stdcall GetInterface(GUID const& id, void** object) = 0;
            };

            auto access = frame.Surface().as<IDirect3DDxgiInterfaceAccess>();
            access->GetInterface(winrt::guid_of<ID3D11Texture2D>(), texture.put_void());
            is_frame_arrived = true;
            return; });
    session.StartCapture();

    // Message pump
    MSG message;
    while (!is_frame_arrived)
    {
        if (PeekMessage(&message, nullptr, 0, 0, PM_REMOVE) > 0)
        {
            DispatchMessage(&message);
        }
    }

    session.Close();

    D3D11_TEXTURE2D_DESC captured_texture_desc;
    texture->GetDesc(&captured_texture_desc);

    captured_texture_desc.Usage = D3D11_USAGE_STAGING;
    captured_texture_desc.BindFlags = 0;
    captured_texture_desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
    captured_texture_desc.MiscFlags = 0;

    winrt::com_ptr<ID3D11Texture2D> user_texture = nullptr;
    winrt::check_hresult(d3d_device->CreateTexture2D(&captured_texture_desc, nullptr, user_texture.put()));

    d3d_context->CopyResource(user_texture.get(), texture.get());
    D3D11_MAPPED_SUBRESOURCE resource;
    winrt::check_hresult(d3d_context->Map(user_texture.get(), NULL, D3D11_MAP_READ, 0, &resource));

    BITMAPINFO l_bmp_info;

    // BMP 32 bpp
    ZeroMemory(&l_bmp_info, sizeof(BITMAPINFO));
    l_bmp_info.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    l_bmp_info.bmiHeader.biBitCount = 32;
    l_bmp_info.bmiHeader.biCompression = BI_RGB;
    l_bmp_info.bmiHeader.biWidth = captured_texture_desc.Width;
    l_bmp_info.bmiHeader.biHeight = captured_texture_desc.Height;
    l_bmp_info.bmiHeader.biPlanes = 1;
    l_bmp_info.bmiHeader.biSizeImage = captured_texture_desc.Width * captured_texture_desc.Height * 4;

    auto p_buf = std::make_unique<BYTE[]>(l_bmp_info.bmiHeader.biSizeImage);
    UINT l_bmp_row_pitch = captured_texture_desc.Width * 4;
    auto sptr = static_cast<BYTE *>(resource.pData);
    auto dptr = p_buf.get() + l_bmp_info.bmiHeader.biSizeImage - l_bmp_row_pitch;

    UINT l_row_pitch = std::min<UINT>(l_bmp_row_pitch, resource.RowPitch);

    for (size_t h = 0; h < captured_texture_desc.Height; ++h)
    {
        memcpy_s(dptr, l_bmp_row_pitch, sptr, l_row_pitch);
        sptr += resource.RowPitch;
        dptr -= l_bmp_row_pitch;
    }
    d3d_context->Unmap(user_texture.get(), NULL);
    BITMAPFILEHEADER bmfh;
    memset(&bmfh, 0, sizeof(BITMAPFILEHEADER));
    bmfh.bfType = 0x4D42; // 'BM'
    bmfh.bfSize = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + l_bmp_info.bmiHeader.biSizeImage;
    bmfh.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

    auto p_buf2 = std::make_unique<BYTE[]>(bmfh.bfSize);
    auto ptr = p_buf2.get();
    memcpy(ptr, &bmfh, sizeof(BITMAPFILEHEADER));
    ptr += sizeof(BITMAPFILEHEADER);
    memcpy(ptr, (char *)&l_bmp_info.bmiHeader, sizeof(BITMAPINFOHEADER));
    ptr += sizeof(BITMAPINFOHEADER);
    memcpy(ptr, p_buf.get(), l_bmp_info.bmiHeader.biSizeImage);
    cb(p_buf2.get(), bmfh.bfSize);
}
void winrt_capture_window(HWND hwnd, void (*cb)(byte *, size_t))
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
