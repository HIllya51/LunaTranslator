// https://github.com/corbamico/get-livecaptions-cpp/
#include <sdkddkver.h>
#include <windows.h>
#include <chrono>
#include <iostream>
#include <fstream>

#include <winrt/windows.ui.uiautomation.h>
#include <uiautomation.h>
#include <wil/resource.h>

using namespace winrt;
using namespace winrt::Windows::Foundation;
using namespace winrt::Windows::UI::UIAutomation;

class Engine
{
    winrt::com_ptr<IUIAutomation> _automation;
    winrt::com_ptr<IUIAutomationCondition> _condition;

public:
    winrt::hstring get_livecaptions()
    {
        wil::unique_bstr text;
        winrt::com_ptr<IUIAutomationElement> window_element;
        winrt::com_ptr<IUIAutomationElement> text_element;

        try
        {
            auto window = FindWindowW(L"LiveCaptionsDesktopWindow", nullptr);
            winrt::check_hresult(_automation->ElementFromHandle(window, window_element.put()));
            winrt::check_hresult(window_element->FindFirst(TreeScope_Descendants, _condition.get(), text_element.put()));
            if (text_element)
            {
                winrt::check_hresult(text_element->get_CurrentName(text.put()));
                return text.get();
            }

            return winrt::hstring();
        }
        catch (winrt::hresult_error &e)
        {
        }
        catch (std::exception &e)
        {
        }
        return winrt::hstring();
    }

    Engine()
    {
        winrt::init_apartment();
        _automation = try_create_instance<IUIAutomation>(guid_of<CUIAutomation>());
        winrt::check_hresult(_automation->CreatePropertyCondition(UIA_AutomationIdPropertyId, wil::make_variant_bstr(L"CaptionsTextBlock"), _condition.put()));
    }
    ~Engine() { winrt::uninit_apartment(); }

    static bool is_livecaption_running()
    {
        return FindWindowW(L"LiveCaptionsDesktopWindow", nullptr) != NULL;
    }
};
DECLARE_API HANDLE livecaption_start(void (*cb)(const wchar_t *))
{
    auto mutex = CreateSemaphoreW(NULL, 0, 1, NULL);
    auto flag = new int{1};
    std::thread([=]()
                {
                    Engine eng;
                    winrt::hstring last;
                    while (*flag)
                    {
                        Sleep(10);
                        if (!Engine::is_livecaption_running())
                            continue;
                        auto hs_current = eng.get_livecaptions();
                        if (hs_current.empty())
                            continue;
                        if(last==hs_current)
                                continue;
                        last=hs_current;
                        cb(hs_current.c_str());
                    } })
        .detach();
    std::thread([=]()
                {
                    WaitForSingleObject(mutex, INFINITE);
                    CloseHandle(mutex);
                    *flag = 0;
                    delete flag; })
        .detach();
    return mutex;
}

DECLARE_API void livecaption_stop(HANDLE m)
{
    ReleaseSemaphore(m, 1, NULL);
}
DECLARE_API bool livecaption_isrunning()
{
    return Engine::is_livecaption_running();
}