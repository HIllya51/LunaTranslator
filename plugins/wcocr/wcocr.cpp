#include <stdafx.h>
#include <wechatocr.h>
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
DECLARE bool wcocr_ocr(void *pobj, const char *u8path, void (*cb)(int, int, int, int, LPCSTR))
{
    if (!pobj)
        return false;
    auto obj = reinterpret_cast<CWeChatOCR *>(pobj);
    CWeChatOCR::result_t res;
    if (!obj->doOCR(u8path, &res))
        return false;
    std::vector<std::wstring> rets;
    std::vector<int> xs, ys, xs2, ys2;
    for (auto &blk : res.ocr_response)
    {
        cb(blk.left, blk.top, blk.right, blk.bottom, blk.text.c_str());
    }
    return true;
}