#include "controls.h"
#include "window.h"
#include <commdlg.h>
control::control(mainwindow *_parent)
{
    if (_parent == 0)
        return;
    parent = _parent;
    parent->controls.push_back(this);
}
void control::dispatch(WPARAM) {}
void control::dispatch_2(WPARAM wParam, LPARAM lParam) {};
button::button(mainwindow *parent) : control(parent) {}
button::button(mainwindow *parent, const std::wstring &text) : control(parent)
{
    winId = CreateWindowEx(0, L"BUTTON", text.c_str(), WS_CHILD | WS_VISIBLE,
                           0, 0, 0, 0, parent->winId, NULL, NULL, NULL);
}
void button::dispatch(WPARAM wparam)
{
    if (wparam == BN_CLICKED)
    {
        onclick();
    }
}
bool checkbox::ischecked()
{
    int state = SendMessage(winId, BM_GETCHECK, 0, 0);
    return (state == BST_CHECKED);
}
checkbox::checkbox(mainwindow *parent, const std::wstring &text) : button(parent)
{
    winId = CreateWindowEx(0, L"BUTTON", text.c_str(), WS_CHILD | WS_VISIBLE | BS_AUTOCHECKBOX | BS_RIGHTBUTTON,
                           0, 0, 0, 0, parent->winId, NULL, NULL, NULL);
}
void checkbox::setcheck(bool b)
{
    SendMessage(winId, BM_SETCHECK, (WPARAM)BST_CHECKED * b, 0);
}
combobox::combobox(mainwindow *parent) : control(parent)
{
    winId = CreateWindowEx(0, L"COMBOBOX", NULL, WS_CHILD | WS_VISIBLE | CBS_DROPDOWNLIST,
                           0, 0, 0, 0, parent->winId, NULL, NULL, NULL);
}
int combobox::additem(const std::wstring &text)
{
    return SendMessage(winId, CB_ADDSTRING, 0, (LPARAM)text.c_str());
}
int combobox::currentidx()
{
    return SendMessage(winId, CB_GETCURSEL, 0, 0);
}
void combobox::setcurrent(int idx)
{
    SendMessage(winId, CB_SETCURSEL, idx, 0);
    if (idx != -1)
        oncurrentchange(idx);
}

void combobox::dispatch(WPARAM wparam)
{
    if (HIWORD(wparam) == CBN_SELCHANGE)
    {
        auto idx = currentidx();
        if (idx != -1)
            oncurrentchange(idx);
    }
}

int spinbox::getcurr()
{
    return SendMessage(hUpDown, UDM_GETPOS32, 0, 0);
}
spinbox::spinbox(mainwindow *parent, int value) : control(parent)
{
    winId = CreateWindowEx(0, L"EDIT", std::to_wstring(value).c_str(), WS_CHILD | WS_VISIBLE | WS_BORDER | ES_NUMBER,
                           0, 0, 0, 0, parent->winId, NULL, NULL, NULL);

    hUpDown = CreateWindowEx(0, UPDOWN_CLASS, NULL,
                             WS_CHILD | WS_VISIBLE | UDS_SETBUDDYINT | UDS_ALIGNRIGHT | UDS_ARROWKEYS | UDS_NOTHOUSANDS,
                             0, 0, 0, 0,
                             parent->winId, NULL, NULL, NULL);
    SendMessage(hUpDown, UDM_SETBUDDY, (WPARAM)winId, 0);
    setminmax(0, 0x7fffffff);
    std::tie(minv, maxv) = getminmax();
}
void spinbox::setgeo(int x, int y, int w, int h)
{
    MoveWindow(winId, x, y, w, h, TRUE);
    SendMessage(hUpDown, UDM_SETBUDDY, (WPARAM)winId, 0);
}
void spinbox::setcurr(int cur)
{
    SendMessage(hUpDown, UDM_SETPOS32, 0, cur);
}
void spinbox::dispatch(WPARAM wparam)
{
    if (HIWORD(wparam) == EN_CHANGE)
    {
        bool ok = false;
        int value;
        try
        {
            value = std::stoi(text());
            ok = true;
        }
        catch (std::exception &)
        {
        }
        if (ok)
        {
            if (value > maxv)
            {
                setcurr(maxv);
                value = maxv;
            }
            else if (value < minv)
            {
                setcurr(minv);
                value = minv;
            }
            else
            {
                onvaluechange(value);
            }
        }
    }
}
std::pair<int, int> spinbox::getminmax()
{
    int minValue, maxValue;
    SendMessage(hUpDown, UDM_GETRANGE32, (WPARAM)&minValue, (LPARAM)&maxValue);
    return {minValue, maxValue};
}
void spinbox::setminmax(int min, int max)
{
    SendMessage(hUpDown, UDM_SETRANGE32, min, max);
    std::tie(minv, maxv) = getminmax();
}
multilineedit::multilineedit(mainwindow *parent) : texteditbase(parent)
{
    winId = CreateWindowEx(0, L"EDIT", L"", WS_CHILD | WS_VISIBLE | WS_BORDER | ES_MULTILINE | ES_AUTOVSCROLL | WS_VSCROLL,
                           0, 0, 0, 0, parent->winId, NULL, NULL, NULL);
    SendMessage(winId, EM_SETLIMITTEXT, 0, 0);
}
std::wstring multilineedit::getsel()
{
    DWORD start, end;
    SendMessage(winId, EM_GETSEL, reinterpret_cast<WPARAM>(&start), reinterpret_cast<LPARAM>(&end));
    int length = end - start;
    return text().substr(start, length);
}
lineedit::lineedit(mainwindow *parent) : texteditbase(parent)
{
    winId = CreateWindowEx(0, L"EDIT", L"", WS_CHILD | WS_VISIBLE | WS_BORDER | ES_AUTOHSCROLL,
                           0, 0, 0, 0, parent->winId, NULL, NULL, NULL);
}
texteditbase::texteditbase(mainwindow *parent) : control(parent) {}
void texteditbase::setreadonly(bool ro)
{
    SendMessage(winId, EM_SETREADONLY, ro, 0);
}
void texteditbase::scrolltoend()
{
    int textLength = GetWindowTextLength(winId);
    SendMessage(winId, EM_SETSEL, (WPARAM)textLength, (LPARAM)textLength);
    SendMessage(winId, EM_SCROLLCARET, 0, 0);
}
void texteditbase::appendtext(const std::wstring &text)
{
    auto _ = std::wstring(L"\r\n") + text;
    SendMessage(winId, EM_REPLACESEL, 0, (LPARAM)_.c_str());
}

void texteditbase::dispatch(WPARAM wparam)
{
    if (HIWORD(wparam) == EN_CHANGE)
    {
        ontextchange(text());
    }
}
label::label(mainwindow *parent, const std::wstring &text) : control(parent)
{
    winId = CreateWindowEx(0, L"STATIC", text.c_str(), WS_CHILD | WS_VISIBLE,
                           0, 0, 0, 0, parent->winId, NULL, NULL, NULL);
}

listbox::listbox(mainwindow *parent) : control(parent)
{

    winId = CreateWindowEx(WS_EX_CLIENTEDGE, L"LISTBOX", L"", WS_CHILD | WS_VISIBLE | WS_VSCROLL | LBS_NOTIFY | LBS_NOINTEGRALHEIGHT,
                           0, 0, 0, 0, parent->winId, NULL, NULL, NULL);
}
void listbox::dispatch(WPARAM wparam)
{
    if (HIWORD(wparam) == LBN_SELCHANGE)
    {
        auto idx = currentidx();
        if (idx != -1)
            oncurrentchange(idx);
    }
}
void listbox::setcurrent(int idx)
{
    SendMessage(winId, LB_SETCURSEL, idx, 0);
    if (idx != -1)
        oncurrentchange(idx);
}
int listbox::currentidx()
{
    return SendMessage(winId, LB_GETCURSEL, 0, 0);
}
std::wstring listbox::text(int idx)
{
    int textLength = SendMessage(winId, LB_GETTEXTLEN, idx, 0);
    std::vector<wchar_t> buffer(textLength + 1);
    SendMessage(winId, LB_GETTEXT, idx, (LPARAM)buffer.data());
    return buffer.data();
}
void listbox::clear()
{
    SendMessage(winId, LB_RESETCONTENT, 0, 0);
}
int listbox::additem(const std::wstring &text)
{
    return SendMessage(winId, LB_ADDSTRING, 0, (LPARAM)text.c_str());
}
void listbox::deleteitem(int i)
{
    SendMessage(winId, LB_DELETESTRING, (WPARAM)i, (LPARAM)i);
}
void listbox::setdata(int idx, LONG_PTR data)
{
    SendMessage(winId, LB_SETITEMDATA, idx, (LPARAM)data);
}
LONG_PTR listbox::getdata(int idx)
{
    return SendMessage(winId, LB_GETITEMDATA, idx, 0);
}
int listbox::count()
{
    return SendMessage(winId, LB_GETCOUNT, 0, 0);
}
int listbox::insertitem(int i, const std::wstring &t)
{
    return SendMessage(winId, LB_INSERTSTRING, i, (LPARAM)t.c_str());
}

void listview::deleteitem(int i)
{
    std::lock_guard _(lockdataidx);
    assodata.erase(assodata.begin() + i);
    for (auto &data : remapidx)
    {
        if (data.second >= i)
            data.second -= 1;
    }
    ListView_DeleteItem(winId, i);
}
listview::listview(mainwindow *parent, bool _addicon, bool notheader) : control(parent), addicon(_addicon)
{
    auto style = WS_VISIBLE | WS_VSCROLL | WS_CHILD | LVS_REPORT | LVS_SINGLESEL;
    if (notheader)
        style |= LVS_NOCOLUMNHEADER;
    winId = CreateWindowEx(0, WC_LISTVIEW, NULL, style, 0, 0, 0, 0, parent->winId, NULL, NULL, NULL);
    ListView_SetExtendedListViewStyle(winId, LVS_EX_FULLROWSELECT); // Set extended styles
    if (addicon)
    {
        hImageList = ImageList_Create(22, 22, // GetSystemMetrics(SM_CXSMICON), GetSystemMetrics(SM_CYSMICON),
                                      ILC_COLOR32, 1, 1);
        ListView_SetImageList(winId, hImageList, LVSIL_SMALL);
    }
}
int listview::insertcol(int i, const std::wstring &text)
{
    LVCOLUMN lvc;
    lvc.mask = LVCF_TEXT;
    lvc.pszText = const_cast<LPWSTR>(text.c_str());
    // lvc.cx = 100;
    return ListView_InsertColumn(winId, i, &lvc);
}
void listview::settext(int row, int col, const std::wstring &text)
{
    ListView_SetItemText(winId, row, col, const_cast<LPWSTR>(text.c_str()));
}
int listview::insertitem(int row, const std::wstring &text, HICON hicon)
{

    LVITEM lvi;
    lvi.pszText = const_cast<LPWSTR>(text.c_str());
    lvi.iItem = row;
    lvi.iSubItem = 0;
    lvi.mask = LVIF_TEXT;
    if (addicon && hicon && hImageList)
    {
        lvi.mask |= LVIF_IMAGE;
        lvi.iImage = ImageList_AddIcon(hImageList, hicon);
    }
    std::lock_guard _(lockdataidx);
    assodata.resize(assodata.size() + 1);
    std::rotate(assodata.begin() + row, assodata.begin() + row + 1, assodata.end());
    for (auto &data : remapidx)
    {
        if (data.second >= row)
            data.second += 1;
    }
    return ListView_InsertItem(winId, &lvi);
}
int listview::additem(const std::wstring &text, HICON hicon)
{
    return insertitem(count(), text, hicon);
}
LONG_PTR listview::getdata(int idx)
{
    std::lock_guard _(lockdataidx);
    return assodata[idx];
}
int listview::querydataidx(LONG_PTR data)
{
    std::lock_guard _(lockdataidx);
    if (remapidx.find(data) == remapidx.end())
        return -1;
    return remapidx[data];
}

void listview::setdata(int idx, LONG_PTR data)
{
    std::lock_guard _(lockdataidx);
    assodata[idx] = data;
    remapidx[data] = idx;
}
void listview::clear()
{
    ListView_DeleteAllItems(winId);
    if (addicon && hImageList)
        ImageList_RemoveAll(hImageList);
}
int listview::count()
{
    return ListView_GetItemCount(winId);
}
int listview::currentidx()
{
    return ListView_GetNextItem(winId, -1, LVNI_SELECTED);
}
void listview::setcurrent(int idx)
{
    ListView_SetItemState(winId, idx, LVIS_SELECTED, LVIS_SELECTED);
}
void listview::dispatch_2(WPARAM wParam, LPARAM lParam)
{
    NMHDR *pnmhdr = (NMHDR *)lParam;
    switch (pnmhdr->code)
    {

    case LVN_ITEMCHANGED:
    {
        NMLISTVIEW *pnmListView = (NMLISTVIEW *)lParam;
        if ((pnmListView->uChanged & LVIF_STATE) && (pnmListView->uNewState & LVIS_SELECTED))
        {
            oncurrentchange(pnmListView->iItem);
        }
        break;
    }
    }
}
std::wstring listview::text(int row, int col)
{
    std::wstring text;
    text.resize(65535);
    LV_ITEM _macro_lvi;
    _macro_lvi.iSubItem = (col);
    _macro_lvi.cchTextMax = (65535);
    _macro_lvi.pszText = (text.data());
    SNDMSG((winId), LVM_GETITEMTEXT, (WPARAM)(row), (LPARAM)(LV_ITEM *)&_macro_lvi);
    return text.c_str();
}
void listview::setheader(const std::vector<std::wstring> &headers)
{
    for (int i = 0; i < headers.size(); i++)
    {
        insertcol(i, headers[i]);
    }
    headernum = headers.size();

    if (headernum == 1)
        ListView_SetColumnWidth(winId, 0, LVSCW_AUTOSIZE_USEHEADER);
    else if (headernum == 2)
    {
        ListView_SetColumnWidth(winId, 0, 0x180);
    }
}
void listview::on_size(int w, int)
{
    if (headernum == 1)
        ListView_SetColumnWidth(winId, 0, LVSCW_AUTOSIZE_USEHEADER);
    else if (headernum == 2)
    {
        auto w0 = ListView_GetColumnWidth(winId, 0);
        ListView_SetColumnWidth(winId, 1, w - w0);
    }
}
void gridlayout::setgeo(int x, int y, int w, int h)
{

    auto dynarow = maxrow;
    auto dynacol = maxcol;
    for (auto fw : fixedwidth)
    {
        dynacol -= 1;
        w -= fw.second + margin;
    }
    for (auto fh : fixedheight)
    {
        dynarow -= 1;
        h -= fh.second + margin;
    }
    auto wpercol = (w - margin * (dynacol + 1)) / dynacol;
    auto hperrow = (h - margin * (dynarow + 1)) / dynarow;

    for (auto ctr : savecontrol)
    {

        int _x = 0, _y = 0, _w = 0, _h = 0;
        for (int c = 0; c < ctr.col + ctr.colrange; c++)
        {
            if (fixedwidth.find(c) != fixedwidth.end())
                if (c < ctr.col)
                    _x += fixedwidth[c];
                else
                    _w += fixedwidth[c];
            else if (c < ctr.col)
                _x += wpercol;
            else
                _w += wpercol;
        }
        _x += (ctr.col + 1) * margin;
        _w += (ctr.colrange - 1) * margin;
        for (int r = 0; r < ctr.row + ctr.rowrange; r++)
        {
            if (fixedheight.find(r) != fixedheight.end())
                if (r < ctr.row)
                    _y += fixedheight[r];
                else
                    _h += fixedheight[r];
            else if (r < ctr.row)
                _y += hperrow;
            else
                _h += hperrow;
        }
        _y += (ctr.row + 1) * margin;
        _h += (ctr.rowrange - 1) * margin;

        ctr.ctr->setgeo(_x, _y, _w, _h);
    }
}
void gridlayout::setfixedwidth(int col, int width)
{
    fixedwidth.insert({col, width});
}
void gridlayout::setfixedheigth(int row, int height)
{
    fixedheight.insert({row, height});
}
void gridlayout::addcontrol(control *_c, int row, int col, int rowrange, int colrange)
{
    maxrow = max(maxrow, row + rowrange);
    maxcol = max(maxcol, col + colrange);
    savecontrol.push_back(
        {_c, row, col, rowrange, colrange});
}
gridlayout::gridlayout(int row, int col) : control(0)
{
    maxrow = row;
    maxcol = col;
    margin = 10;
}
void gridlayout::setmargin(int m)
{
    margin = m;
}
void Menu::dispatch(WPARAM wparam)
{
    auto idx = LOWORD(wparam);
    menu_callbacks[idx].callback();
    DestroyMenu(hmenu);
}
HMENU Menu::load()
{
    hmenu = CreatePopupMenu();
    for (int i = 0; i < menu_callbacks.size(); i++)
    {
        AppendMenuW(hmenu, menu_callbacks[i].type, i, menu_callbacks[i].str.c_str());
    }
    return hmenu;
}
void Menu::add(const std::wstring &str, std::function<void()> callback)
{
    menu_callbacks.push_back({MF_STRING, callback, str});
}
void Menu::add_checkable(const std::wstring &str, bool check, std::function<void(bool)> callback)
{
    menu_callbacks.push_back({(UINT)(MF_STRING | (check ? MF_CHECKED : MF_UNCHECKED)), std::bind(callback, !check), str});
}
void Menu::add_sep()
{
    menu_callbacks.push_back({MF_SEPARATOR});
}
FontSelector::FontSelector(HWND hwnd, const Font &font, std::function<void(const Font &)> callback)
{
    CHOOSEFONTW cf;
    ZeroMemory(&cf, sizeof(CHOOSEFONTW));
    LOGFONT lf = font.logfont();
    cf.lStructSize = sizeof(CHOOSEFONTW);
    cf.hwndOwner = hwnd;
    cf.lpLogFont = &lf;
    cf.Flags = CF_INITTOLOGFONTSTRUCT | CF_SCREENFONTS; // | CF_EFFECTS;
    if (ChooseFontW(&cf))
    {
        Font f{lf.lfFaceName, cf.iPointSize / 10.0f, !!(cf.nFontType & BOLD_FONTTYPE), !!(cf.nFontType & ITALIC_FONTTYPE)};
        callback(f);
    }
}