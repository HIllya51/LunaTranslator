#include <stdafx.h>
#include <wechatocr.h>
#define DECLARE_API extern "C" __declspec(dllexport)

DECLARE_API void *wcocr_init(const wchar_t *wexe, const wchar_t *wwcdir)
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

DECLARE_API void wcocr_destroy(CWeChatOCR *pobj)
{
    if (!pobj)
        return;
    delete pobj;
}
DECLARE_API bool wcocr_ocr(CWeChatOCR *pobj, const char *u8path, void (*cb)(float, float, float, float, LPCSTR))
{
    if (!pobj)
        return false;
    CWeChatOCR::result_t res;
    if (!pobj->doOCR(u8path, &res))
        return false;
    for (auto &blk : res.ocr_response)
    {
        cb(blk.left, blk.top, blk.right, blk.bottom, blk.text.c_str());
    }
    return true;
}