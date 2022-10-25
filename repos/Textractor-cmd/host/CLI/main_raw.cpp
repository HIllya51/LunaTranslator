#include "../host.h"
#include "../hookcode.h"
#include <io.h>
#include <fcntl.h>
#include <iostream>

int main()
{
	_setmode(_fileno(stdout), _O_U16TEXT);
	_setmode(_fileno(stdin), _O_U16TEXT);
	wprintf_s(L"Usage: {'attach'|'detach'|hookcode} -Pprocessid\n");
	fflush(stdout);
	Host::Start([](auto) {}, [](auto) {}, [](auto&) {}, [](auto&) {}, [](TextThread& thread, std::wstring& output)
		{
			wprintf_s(L"[%I64X:%I32X:%I64X:%I64X:%I64X:%s:%s] %s\n",
				thread.handle,
				thread.tp.processId,
				thread.tp.addr,
				thread.tp.ctx,
				thread.tp.ctx2,
				thread.name.c_str(),
				HookCode::Generate(thread.hp, thread.tp.processId).c_str(),
				output.c_str()
			);
			fflush(stdout);
			return false;
		});
	wchar_t input[500] = {};
	while (fgetws(input, 500, stdin))
	{
		wchar_t command[500] = {};
		DWORD processId = 0;
		if (swscanf(input, L"%500s -P%d", command, &processId) != 2) ExitProcess(0);
		if (_wcsicmp(command, L"attach") == 0) Host::InjectProcess(processId);
		else if (_wcsicmp(command, L"detach") == 0) Host::DetachProcess(processId);
		else if (auto hp = HookCode::Parse(command)) Host::InsertHook(processId, hp.value());
		else ExitProcess(0);
	}
	ExitProcess(0);
}
