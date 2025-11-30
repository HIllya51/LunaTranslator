//=====================================================================
//
// PyStand.h -
//
// Created by skywind on 2022/02/03
// Last Modified: 2022/02/03 23:39:52
//
//=====================================================================
#ifndef _PYSTAND_H_
#define _PYSTAND_H_
#include <windows.h>

#ifndef E_BOUNDS
#define E_BOUNDS _HRESULT_TYPEDEF_(0x8000000BL)
#endif

#include <string>
#include <set>
#include <vector>
//---------------------------------------------------------------------
// PyStand
//---------------------------------------------------------------------
class PyStand
{
public:
	virtual ~PyStand();
	PyStand(const wchar_t *runtime);

public:
	int RunString(const wchar_t *script);
	int DetectScript();

	std::wstring exepath;
	bool checkintegrity();
	std::set<const wchar_t *> checkintegrity_(bool & succ);

protected:
	bool CheckEnviron(const wchar_t *rtp);
	bool LoadPython();

protected:
	typedef int (*t_Py_Main)(int argc, wchar_t **argv);
	t_Py_Main _Py_Main;

protected:
	HINSTANCE _hDLL;
	std::wstring _args;	   // arguments
	std::wstring _runtime; // absolute path of embedded python runtime
	std::wstring _home;	   // home directory of PyStand.exe
	std::vector<std::wstring> _argv;
	std::vector<std::wstring> _py_argv;
	std::vector<wchar_t *> _py_args;
};

#endif
