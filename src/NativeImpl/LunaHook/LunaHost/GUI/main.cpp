#include "LunaHost.h"
int main()
{
    SetProcessDPIAware();
    LunaHost _lunahost;
    _lunahost.show();
    mainwindow::run();
}
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
    main();
}