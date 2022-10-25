#include "../host.h"
#include "../hookcode.h"
#include <io.h>
#include <fcntl.h>
#include <iostream>

int main()
{
	_setmode(_fileno(stdout), _O_U16TEXT);
	_setmode(_fileno(stdin), _O_U16TEXT);
	SearchParam sp = {};
	sp.codepage = Host::defaultCodepage;
	sp.length = 0;
	DWORD processId = 14332;
	wprintf_s(L"1\n");
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
	auto hooks = std::make_shared<std::vector<std::wstring>>();
	wprintf_s(L"2\n");
	Host::InjectProcess(processId);
	wprintf_s(L"4\n");
		Host::FindHooks(processId, sp,
			[hooks](HookParam hp, std::wstring text) { 
				hooks->push_back(HookCode::Generate(hp) + L" => " + text);
				wprintf_s(L"%s \n", HookCode::Generate(hp) + L" => " + text);
			});
	 
		wprintf_s(L"3\n");
		scanf_s("1");
	return 0;
}
