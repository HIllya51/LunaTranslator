#include <stdafx.h>
#include <wechatocr.h>
#include <nlohmann/json.hpp>
#define DECLARE extern "C" __declspec(dllexport)

DECLARE void *wcocr_init(const wchar_t *wexe, const wchar_t *wwcdir)
{
    auto obj = new CWeChatOCR(wexe, wwcdir);
    if (obj->wait_connection(5000))
    {
        return obj;
    }
    else
    {
        delete obj;
        return nullptr;
    }
}

DECLARE void wcocr_destroy(void *pobj)
{
    if (!pobj)
        return;
    auto obj = reinterpret_cast<CWeChatOCR *>(pobj);
    delete obj;
}
DECLARE void wcocr_free_str(char *ptr)
{
    delete[] ptr;
}
DECLARE char *wcocr_ocr(void *pobj, const char *u8path)
{
    if (!pobj)
        return 0;
    auto obj = reinterpret_cast<CWeChatOCR *>(pobj);
    CWeChatOCR::result_t res;
    std::string imgpath = u8path;
    if (!obj->doOCR(imgpath, &res))
        return 0;
    std::vector<std::wstring> rets;
    std::vector<int> xs, ys, xs2, ys2;
    nlohmann::json js;
    for (auto &blk : res.ocr_response)
    {
        js.push_back({blk.left, blk.top, blk.right, blk.bottom, blk.text});
    }
    std::string _s = js.dump();
    auto s = new char[_s.size() + 1];
    strcpy(s, _s.c_str());
    return s;
}