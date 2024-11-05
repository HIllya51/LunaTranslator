

class Abel : public ENGINE
{
public:
    Abel()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            // jichi 8/24/2013: Move into functions
            // Artikash 6/15/2018: Removed this detection for Abel Software games. IthGetFileInfo no longer works correctly
            // static BYTE static_file_info[0x1000];
            // if (IthGetFileInfo(L"*01", static_file_info))
            //  if (*(DWORD*)static_file_info == 0) {
            //    STATUS_INFO_LENGTH_MISMATCH;
            //    static WCHAR static_search_name[MAX_PATH];
            //    LPWSTR name=(LPWSTR)(static_file_info+0x5E);
            //    int len = wcslen(name);
            //    name[len-2] = L'.';
            //    name[len-1] = L'e';
            //    name[len] = L'x';
            //    name[len+1] = L'e';
            //    name[len+2] = 0;
            //    if (Util::CheckFile(name)) {
            //  sizeof(FILE_BOTH_DIR_INFORMATION);
            //      name[len-2] = L'*';
            //      name[len-1] = 0;
            //      wcscpy(static_search_name,name);
            //      IthGetFileInfo(static_search_name,static_file_info);
            //      union {
            //        FILE_BOTH_DIR_INFORMATION *both_info;
            //        DWORD addr;
            //      };
            //      both_info = (FILE_BOTH_DIR_INFORMATION *)static_file_info;
            //      //BYTE* ptr=static_file_info;
            //      len=0;
            //      while (both_info->NextEntryOffset) {
            //        addr += both_info->NextEntryOffset;
            //        len++;
            //      }
            //      if (len > 3) {
            //        InsertAbelHook();
            //        return true;
            //      }
            //    }
            //  }
            return (Util::CheckFile(L"system") && Util::CheckFile(L"system.dat")) || Util::CheckFile(L"*01");
        };

        is_engine_certain = false;
    };
    bool attach_function();
};