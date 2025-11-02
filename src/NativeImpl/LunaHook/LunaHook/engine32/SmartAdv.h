/*
smartadv.dll->
    BLOCK "StringFileInfo"
  {
    BLOCK "041103a4"
    {
      VALUE "CompanyName",       "F&C Co.,Ltd."
      VALUE "FileDescription",   "Scenario Script Engine "SmartAdv""
      VALUE "FileVersion",       "1.0.0.639"
      VALUE "InternalName",      "Scenario Script Engine"
      VALUE "LegalCopyright",    "Copyright (C) 2005-2007 F&C Co.,Ltd."
      VALUE "ProductName",       "SmartAdv"
    }
  }
*/
/*
EXE->
BLOCK "StringFileInfo"
  {
    BLOCK "041103a4"
    {
      VALUE "CompanyName",       "F&C Co.,Ltd."
      VALUE "FileDescription",   "Advanced System "Overture""
      VALUE "FileVersion",       "0.0.0.2001"
      VALUE "InternalName",      "NS-00 (Code: Zero-System)"
      VALUE "LegalCopyright",    "Copyright (C) 2005-2007 F&C Co.,Ltd."
      VALUE "ProductName",       "Overture"
    }
  }

*/
class SmartAdv : public ENGINE
{
public:
    SmartAdv()
    {
        enginename = "Scenario Script Engine";
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto smartadv = GetModuleHandle(L"smartadv.dll");
            auto video = GetModuleHandle(L"video.dll");
            auto NSL = GetModuleHandle(L"NSL.dll");
            if (!smartadv || !video || !NSL)
                return false;
            return Util::SearchResourceString(L"Scenario Script Engine", smartadv);
        };
    };
    bool attach_function();
};