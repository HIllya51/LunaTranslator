#include <Windows.h>
#include <iostream>
#include <string>
extern "C"
{
    typedef int(__stdcall *MTInitCJ)(int);
    typedef int(__stdcall *TranTextFlowCJ)(char *src, char *dest, int, int);
}
std::string WStrToStr(wchar_t *xx, UINT uCodePage)
{
    std::wstring wstrString = xx;
    int lenStr = 0;
    std::string result;

    lenStr = WideCharToMultiByte(uCodePage, NULL, wstrString.c_str(), wstrString.size(), NULL, NULL, NULL, NULL);
    char *buffer = new char[lenStr + 1];
    WideCharToMultiByte(uCodePage, NULL, wstrString.c_str(), wstrString.size(), buffer, lenStr, NULL, NULL);
    buffer[lenStr] = '\0';

    result.append(buffer);
    delete[] buffer;
    return result;
}
#include <vector>
std::wstring StringToWideString(const std::string &text, UINT encoding)
{
    std::vector<wchar_t> buffer(text.size() + 1);
    int length = MultiByteToWideChar(encoding, 0, text.c_str(), text.size() + 1, buffer.data(), buffer.size());
    return std::wstring(buffer.data(), length - 1);
}

int dreyewmain(int argc, wchar_t *argv[])
{
    SetCurrentDirectory(argv[1]);
    HMODULE h = LoadLibrary(argv[2]);
    /*wchar_t* apiinit = argv[3];
    wchar_t* apitrans = argv[4];*/
    if (h)
    {

        MTInitCJ _MTInitCJ;
        TranTextFlowCJ _TranTextFlowCJ;
        if (_wtoi(argv[3]) == 3 || _wtoi(argv[3]) == 10)
        {
            _MTInitCJ = (MTInitCJ)GetProcAddress(h, "MTInitCJ");                   // WStrToStr(apiinit, 936).c_str());
            _TranTextFlowCJ = (TranTextFlowCJ)GetProcAddress(h, "TranTextFlowCJ"); // WStrToStr(apitrans, 936).c_str());
        }
        else
        {
            _MTInitCJ = (MTInitCJ)GetProcAddress(h, "MTInitEC");                   // WStrToStr(apiinit, 936).c_str());
            _TranTextFlowCJ = (TranTextFlowCJ)GetProcAddress(h, "TranTextFlowEC"); // WStrToStr(apitrans, 936).c_str());
        }

        _MTInitCJ(_wtoi(argv[3]));

        HANDLE hPipe = CreateNamedPipe(argv[4], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);
        SECURITY_DESCRIPTOR sd = {};
        InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
        SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
        SECURITY_ATTRIBUTES allAccess = SECURITY_ATTRIBUTES{sizeof(SECURITY_ATTRIBUTES), &sd, FALSE};
        SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[5]));
        if (ConnectNamedPipe(hPipe, NULL) != NULL)
        {
            DWORD len = 0;
        }
        while (true)
        {
            char src[4096] = {0};
            char buffer[3000] = {0};
            DWORD _;
            if (!ReadFile(hPipe, src, 4096, &_, NULL))
                break;

            _TranTextFlowCJ(src, buffer, 3000, _wtoi(argv[3]));
            // MessageBoxW(0, StringToWideString(src,932).c_str(),L"", 0);
            StringToWideString(src, 932); //?????��ȫ�㲻��������仰ȥ����writefile��д����ȥ�ˡ�����
            WriteFile(hPipe, buffer, strlen(buffer), &_, NULL);
        }
    }
    return 0;
}