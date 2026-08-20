// https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-select-audio-input-devices

#include <cstdio>
#include <mmdeviceapi.h>
#include <setupapi.h>
#include <devguid.h>
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
    for (ULONG i = 0; i < count; i++)
    {
        // Get the pointer to endpoint number i.
        CHECK_FAILURE_NORET(pCollection->Item(i, &pEndpoint));

        // Get the endpoint ID string.
        CHECK_FAILURE_NORET(pEndpoint->GetId(&pwszID));

        CHECK_FAILURE_NORET(pEndpoint->OpenPropertyStore(
            STGM_READ, &pProps));

        // Initialize the container for property value.
        AutoPropVariant varName;
        // Get the endpoint's friendly-name property.
        CHECK_FAILURE_NORET(pProps->GetValue(PKEY_Device_FriendlyName, &varName));

        // Print the endpoint friendly name and endpoint ID.
        cb(varName->pwszVal, pwszID);
    }
}
DECLARE_API void ListXpuVendors(bool gpu, void (*cb)(LPCWSTR))
{
    HDEVINFO deviceInfoSet = SetupDiGetClassDevs(
        gpu ? &GUID_DEVCLASS_DISPLAY : &GUID_DEVCLASS_COMPUTEACCELERATOR,
        NULL,
        NULL,
        DIGCF_PRESENT);

    if (deviceInfoSet == INVALID_HANDLE_VALUE)
        return;

    SP_DEVINFO_DATA deviceInfoData;
    deviceInfoData.cbSize = sizeof(SP_DEVINFO_DATA);
    DWORD deviceIndex = 0;

    while (SetupDiEnumDeviceInfo(deviceInfoSet, deviceIndex, &deviceInfoData))
    {
        deviceIndex++;

        auto find = [](const std::wstring &buffer) -> std::optional<std::wstring>
        {
            auto currentId = buffer.data();
            while (*currentId)
            {
                std::wstring hwId(currentId);
                size_t venPos = hwId.find(L"VEN_");
                if (venPos != std::wstring::npos)
                {
                    std::wstring venCode = hwId.substr(venPos + 4, 4);
                    std::transform(venCode.begin(), venCode.end(), venCode.begin(), ::towupper);
                    return venCode;
                }
                currentId += wcslen(currentId) + 1;
            }
            return {};
        };

        wchar_t hardwareId[MAX_PATH] = {0};
        if (!SetupDiGetDeviceRegistryProperty(
                deviceInfoSet,
                &deviceInfoData,
                SPDRP_HARDWAREID,
                NULL,
                (PBYTE)hardwareId,
                sizeof(hardwareId),
                NULL))
            continue;

        auto vendorid = find(hardwareId);
        if (!vendorid)
            continue;
        cb(vendorid.value().c_str());
    }

    SetupDiDestroyDeviceInfoList(deviceInfoSet);
}