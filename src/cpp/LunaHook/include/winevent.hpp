#include <Windows.h>
class win_event
{
  typedef win_event _Self;
  typedef HANDLE __native_handle_type;
  typedef const char *__native_string_type;

  __native_handle_type _M_handle;
  __native_string_type _M_name;

  win_event(const _Self &);
  _Self &operator=(const _Self &);

public:
  typedef __native_handle_type native_handle_type;
  typedef __native_string_type native_string_type;

  explicit win_event(native_string_type name, bool create = true)
      : _M_name(name)
  {
    _M_handle = create ? // lpEventAttributes, bManualReset, bInitialState, lpName
                    ::CreateEventA(nullptr, TRUE, FALSE, name)
                       : ::OpenEventA(EVENT_ALL_ACCESS, FALSE, name); // dwDesiredAccess,  bInheritHandle, lpName
  }

  ~win_event() { ::CloseHandle(_M_handle); }

  native_handle_type native_handle() const { return _M_handle; }
  native_string_type native_name() const { return _M_name; }

  bool valid() const { return _M_handle; }

  bool signal(bool t)
  {
    return t ? ::SetEvent(_M_handle) : ::ResetEvent(_M_handle);
  }

  ///  Return true only if when it is wake up by notify instead of timeout
  bool wait(DWORD msec = INFINITE)
  {
    return WAIT_OBJECT_0 == ::WaitForSingleObject(_M_handle, msec);
  }
};
