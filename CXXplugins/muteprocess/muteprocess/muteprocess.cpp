// muteprocess.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <Audiopolicy.h>
#include <iostream>
#include<string> 
#include <mmdeviceapi.h>
#include <Psapi.h> 
#include<Windows.h>
#include <atlbase.h>
 
#pragma comment(lib, "Psapi.lib")

class CAudioMgr
{
public:
    CAudioMgr();
    ~CAudioMgr();

public:
    HRESULT GetHResult() const { return m_hRes; } 
    BOOL    SetProcessMute(DWORD Pid,bool mute);

private:
    BOOL    __GetAudioSessionMgr2();

private:
    HRESULT                 m_hRes;
    IAudioSessionManager2* m_lpAudioSessionMgr;
};

CAudioMgr::CAudioMgr()
    : m_hRes(ERROR_SUCCESS)
    , m_lpAudioSessionMgr(NULL)
{
    ::CoInitialize(NULL);
}

CAudioMgr::~CAudioMgr()
{
    ::CoUninitialize();
}

BOOL CAudioMgr::SetProcessMute(DWORD Pid,bool mute)
{
    if (!this->__GetAudioSessionMgr2() || m_lpAudioSessionMgr == NULL)
    {
        return FALSE;
    }

    CComPtr<IAudioSessionEnumerator> pAudioSessionEnumerator;
    m_hRes = m_lpAudioSessionMgr->GetSessionEnumerator(&pAudioSessionEnumerator);
    if (FAILED(m_hRes) || pAudioSessionEnumerator == NULL)
    {
        return FALSE;
    }

    int nCount = 0;
    m_hRes = pAudioSessionEnumerator->GetCount(&nCount);

    for (int i = 0; i < nCount; ++i)
    {
        CComPtr<IAudioSessionControl> pAudioSessionControl;
        m_hRes = pAudioSessionEnumerator->GetSession(i, &pAudioSessionControl);
        if (FAILED(m_hRes) || pAudioSessionControl == NULL)
        {
            continue;
        }

        CComQIPtr<IAudioSessionControl2> pAudioSessionControl2(pAudioSessionControl);
        if (pAudioSessionControl2 == NULL)
        {
            continue;
        }

        DWORD dwPid = 0;
        m_hRes = pAudioSessionControl2->GetProcessId(&dwPid);
        if (FAILED(m_hRes))
        {
            continue;
        }

        if (dwPid == Pid)
        {
            CComQIPtr<ISimpleAudioVolume> pSimpleAudioVolume(pAudioSessionControl2);
            if (pSimpleAudioVolume == NULL)
            {
                continue;
            } 
            m_hRes = pSimpleAudioVolume->SetMute(mute, NULL);
            break;
        }
    }

    return SUCCEEDED(m_hRes);
}
 

BOOL CAudioMgr::__GetAudioSessionMgr2()
{
    if (m_lpAudioSessionMgr == NULL)
    {
        CComPtr<IMMDeviceEnumerator> pMMDeviceEnumerator;

        m_hRes = pMMDeviceEnumerator.CoCreateInstance(__uuidof(MMDeviceEnumerator), NULL, CLSCTX_ALL);
        if (FAILED(m_hRes) || (pMMDeviceEnumerator == NULL))
        {
            return FALSE;
        }

        CComPtr<IMMDevice> pDefaultDevice;
        m_hRes = pMMDeviceEnumerator->GetDefaultAudioEndpoint(eRender, eConsole, &pDefaultDevice);
        if (FAILED(m_hRes) || pDefaultDevice == NULL)
        {
            return FALSE;
        }

        m_hRes = pDefaultDevice->Activate(__uuidof(IAudioSessionManager2), CLSCTX_ALL, NULL, (void**)&m_lpAudioSessionMgr);
        if (FAILED(m_hRes) || (m_lpAudioSessionMgr == NULL))
        {
            return FALSE;
        }
    }

    return TRUE;
}
int main(int argc,char*argv[])
{ 
    CAudioMgr AudioMgr;
    AudioMgr.SetProcessMute(atoi(argv[1]), atoi(argv[2]));
}

// 运行程序: Ctrl + F5 或调试 >“开始执行(不调试)”菜单
// 调试程序: F5 或调试 >“开始调试”菜单

// 入门使用技巧: 
//   1. 使用解决方案资源管理器窗口添加/管理文件
//   2. 使用团队资源管理器窗口连接到源代码管理
//   3. 使用输出窗口查看生成输出和其他消息
//   4. 使用错误列表窗口查看错误
//   5. 转到“项目”>“添加新项”以创建新的代码文件，或转到“项目”>“添加现有项”以将现有代码文件添加到项目
//   6. 将来，若要再次打开此项目，请转到“文件”>“打开”>“项目”并选择 .sln 文件
