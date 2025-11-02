#ifndef LUNA_BASE_CONTROLS_H
#define LUNA_BASE_CONTROLS_H
#include "window.h"
#include <CommCtrl.h>
class Menu
{
public:
    void dispatch(WPARAM);
    struct menuinfos
    {
        UINT type;
        std::function<void()> callback;
        std::wstring str;
    };
    std::vector<menuinfos> menu_callbacks;
    HMENU load();
    HMENU hmenu;
    void add(const std::wstring &, std::function<void()> callback);
    void add_checkable(const std::wstring &, bool, std::function<void(bool)> callback);
    void add_sep();
};
using maybehavemenu = std::optional<Menu>;

class control : public basewindow
{
public:
    mainwindow *parent;
    control(mainwindow *);
    virtual void dispatch(WPARAM);
    virtual void dispatch_2(WPARAM wParam, LPARAM lParam);
    maybehavemenu menu;
    std::function<maybehavemenu()> on_menu = []() -> maybehavemenu
    { return {}; };
};

class button : public control
{
public:
    button(mainwindow *parent);
    button(mainwindow *, const std::wstring &); //,int,int,int,int,DWORD=BS_PUSHBUTTON);
    void dispatch(WPARAM);
    std::function<void()> onclick = []() {};
};
class checkbox : public button
{
public:
    checkbox(mainwindow *, const std::wstring &); //,int,int,int,int);
    bool ischecked();
    void setcheck(bool);
};
class texteditbase : public control
{
public:
    texteditbase(mainwindow *);
    void dispatch(WPARAM);
    std::function<void(const std::wstring &)> ontextchange = [&](const std::wstring &text) {};
    void appendtext(const std::wstring &);
    void scrolltoend();
    void setreadonly(bool);
};
class multilineedit : public texteditbase
{
public:
    multilineedit(mainwindow *);
    std::wstring getsel();
};
class lineedit : public texteditbase
{
public:
    lineedit(mainwindow *);
};
class spinbox : public control
{
    HWND hUpDown;
    int minv, maxv;

public:
    void dispatch(WPARAM);
    spinbox(mainwindow *, int);
    void setminmax(int, int);
    std::pair<int, int> getminmax();
    void setcurr(int);
    int getcurr();
    std::function<void(int)> onvaluechange = [&](int) {};
    void setgeo(int, int, int, int);
};
class label : public control
{
public:
    label(mainwindow *, const std::wstring &);
};

class combobox : public control
{
public:
    combobox(mainwindow *);
    int additem(const std::wstring &);
    int currentidx();
    void dispatch(WPARAM);
    void setcurrent(int idx);
    std::function<void(int)> oncurrentchange = [](int) {};
};
class listbox : public control
{
public:
    listbox(mainwindow *);
    void dispatch(WPARAM);
    int currentidx();
    std::wstring text(int);
    std::function<void(int)> oncurrentchange = [](int) {};
    void clear();
    int additem(const std::wstring &);
    void deleteitem(int);
    void setdata(int, LONG_PTR);
    void setcurrent(int idx);
    int insertitem(int, const std::wstring &);
    LONG_PTR getdata(int);
    int count();
};
class listview : public control
{
    int headernum = 1;
    bool addicon;
    HIMAGELIST hImageList;
    std::vector<LONG_PTR> assodata;
    std::map<LONG_PTR, int> remapidx;
    std::mutex lockdataidx;

public:
    listview(mainwindow *, bool, bool);
    int insertitem(int, const std::wstring &, HICON hicon = NULL);
    void settext(int, int, const std::wstring &);
    int insertcol(int, const std::wstring &);
    void clear();
    int count();
    int currentidx();
    void setcurrent(int idx);

    std::function<void(int)> oncurrentchange = [](int) {};
    std::wstring text(int, int = 0);
    void setheader(const std::vector<std::wstring> &);
    void deleteitem(int);
    int additem(const std::wstring &, HICON hicon = NULL);
    LONG_PTR getdata(int);
    void setdata(int, LONG_PTR);
    int querydataidx(LONG_PTR);
    void dispatch_2(WPARAM wParam, LPARAM lParam);
    void on_size(int, int);
};
class gridlayout : public control
{
    struct _c
    {
        control *ctr;
        int row, col, rowrange, colrange;
    };
    int margin;
    int maxrow, maxcol;
    std::vector<_c> savecontrol;
    std::map<int, int> fixedwidth, fixedheight;

public:
    void setgeo(int, int, int, int);
    void setfixedwidth(int col, int width);
    void setfixedheigth(int row, int height);
    void addcontrol(control *, int row, int col, int rowrange = 1, int colrange = 1);
    gridlayout(int row = 0, int col = 0);
    void setmargin(int m = 10);
};
class FontSelector
{
public:
    FontSelector(HWND hwnd, const Font &, std::function<void(const Font &)> callback);
};
#endif