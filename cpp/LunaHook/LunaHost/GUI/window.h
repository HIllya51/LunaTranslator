#ifndef LUNA_BASE_WINDOW_H
#define LUNA_BASE_WINDOW_H
class control;
class basewindow
{
public:
    HWND winId;
    virtual void setgeo(int, int, int, int);
    virtual void on_size(int w, int h);
    RECT getgeo();
    std::wstring text();
    void settext(const std::wstring &);
    operator HWND() { return winId; }
};

struct Font
{
    std::wstring fontfamily;
    float fontsize;
    bool bold;
    bool italic;
    float calc_height() const
    {
        return MulDiv(fontsize, GetDeviceCaps(GetDC(NULL), LOGPIXELSY), 72);
    }
    HFONT hfont() const
    {
        return CreateFontIndirect(&logfont());
    }
    LOGFONT logfont() const
    {
        LOGFONT lf;
        ZeroMemory(&lf, sizeof(LOGFONT));
        wcscpy_s(lf.lfFaceName, fontfamily.c_str());
        if (bold)
            lf.lfWeight = FW_BOLD;
        lf.lfItalic = italic;
        lf.lfHeight = calc_height();
        return lf;
    }
};
class mainwindow : public basewindow
{
    HFONT hfont = 0;

public:
    void setfont(const Font &);
    void visfont();
    std::vector<control *> controls;
    std::vector<mainwindow *> childrens;
    mainwindow *parent;
    HWND lastcontexthwnd;
    control *layout;
    virtual void on_show();
    virtual void on_close();
    void on_size(int w, int h);
    mainwindow(mainwindow *_parent = 0);
    LRESULT wndproc(UINT message, WPARAM wParam, LPARAM lParam);
    static void run();
    void show();
    void close();
    void setcentral(int, int);
    std::pair<int, int> calculateXY(int w, int h);
    void setlayout(control *);
};
HICON GetExeIcon(const std::wstring &filePath);
#endif