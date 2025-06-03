// https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-select-audio-input-devices

#include <cstdio>
#include <mmdeviceapi.h>

#include <Functiondiscoverykeys_devpkey.h>

const CLSID CLSID_MMDeviceEnumerator = __uuidof(MMDeviceEnumerator);
const IID IID_IMMDeviceEnumerator = __uuidof(IMMDeviceEnumerator);

constexpr auto REFTIMES_PER_SEC = (10000000 * 25);
constexpr auto REFTIMES_PER_MILLISEC = 10000;

//-----------------------------------------------------------
// This function enumerates all active (plugged in) audio
// rendering endpoint devices. It prints the friendly name
// and endpoint ID string of each endpoint device.
//-----------------------------------------------------------
DECLARE_API void ListEndpoints(bool input, void (*cb)(LPCWSTR, LPCWSTR))
{
    CO_INIT co;
    CComPtr<IMMDeviceEnumerator> pEnumerator = NULL;
    CComPtr<IMMDeviceCollection> pCollection = NULL;
    CComPtr<IMMDevice> pEndpoint = NULL;
    CComPtr<IPropertyStore> pProps = NULL;
    CComHeapPtr<WCHAR> pwszID;
    CHECK_FAILURE_NORET(CoCreateInstance(CLSID_MMDeviceEnumerator, NULL, CLSCTX_ALL, IID_IMMDeviceEnumerator, (void **)&pEnumerator))

    CHECK_FAILURE_NORET(pEnumerator->EnumAudioEndpoints(input ? eCapture : eRender, DEVICE_STATE_ACTIVE, &pCollection));

    UINT count;
    CHECK_FAILURE_NORET(pCollection->GetCount(&count));
    // Each iteration prints the name of an endpoint device.
    PROPVARIANT varName;
    for (ULONG i = 0; i < count; i++)
    {
        // Get the pointer to endpoint number i.
        CHECK_FAILURE_NORET(pCollection->Item(i, &pEndpoint));

        // Get the endpoint ID string.
        CHECK_FAILURE_NORET(pEndpoint->GetId(&pwszID));

        CHECK_FAILURE_NORET(pEndpoint->OpenPropertyStore(
            STGM_READ, &pProps));

        // Initialize the container for property value.
        PropVariantInit(&varName);
        struct __onexits
        {
            PROPVARIANT varName;
            ~__onexits()
            {
                PropVariantClear(&varName);
            }
        };
        __onexits __{varName};
        // Get the endpoint's friendly-name property.
        CHECK_FAILURE_NORET(pProps->GetValue(PKEY_Device_FriendlyName, &varName));

        // Print the endpoint friendly name and endpoint ID.
        cb(varName.pwszVal, pwszID);
    }
}