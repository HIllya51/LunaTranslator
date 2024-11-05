#include "host.h"
#include <io.h>
#include <fcntl.h>

int main()
{
	_setmode(_fileno(stdout), _O_U16TEXT);
	_setmode(_fileno(stdin), _O_U16TEXT);
	wprintf_s(L"Usage: {'attach'|'detach'|hookcode} -Pprocessid\n");
	fflush(stdout);
	Host::Start([](auto) {}, [](auto) {}, [](auto &) {}, [](auto &) {}, [](TextThread &thread, std::wstring &output)
				{
			wprintf_s(L"[%I64X:%I32X:%I64X:%I64X:%I64X:%s:%s] %s\n",
				thread.handle,
				thread.tp.processId,
				thread.tp.addr,
				thread.tp.ctx,
				thread.tp.ctx2,
				thread.name.c_str(),
				thread.hp.hookcode,
				output.c_str()
			);
			fflush(stdout);
			return false; });
	wchar_t input[500] = {};
	SearchParam sp = {};
	sp.codepage = Host::defaultCodepage;
	sp.length = 0;
	while (fgetws(input, 500, stdin))
	{
		if (wcslen(input) <= 1)
			continue; //\r\n，第二行会直接只有一个\n
		wchar_t command[500] = {};
		DWORD processId = 0;

		int split;
		for (split = wcslen(input) - 1; split >= 1; split--)
		{
			if (input[split] == L'P' && input[split - 1] == '-')
			{
				processId = _wtoi(input + split + 1);
				break;
			}
		}
		if (split == 1)
			continue; // ExitProcess(0);
		split -= 2;
		while (split > 0 && input[split] == L' ')
			split -= 1;
		if (split == 0)
			continue; // ExitProcess(0);
		input[split + 1] = 0;
		wcscpy(command, input);
		// if (swscanf(input, L"%500s -P%d", command, &processId) != 2) ExitProcess(0);
		if (_wcsicmp(command, L"attach") == 0)
			Host::InjectProcess(processId);
		else if (_wcsicmp(command, L"detach") == 0)
		{
			Host::DetachProcess(processId);
		}
		else if (_wcsicmp(command, L"find") == 0)
		{
			std::shared_ptr<std::vector<std::wstring>> hooks = std::make_shared<std::vector<std::wstring>>();

			try
			{
				Host::FindHooks(processId, sp,
								[hooks](HookParam hp, std::wstring text)
								{
									// if (std::regex_search(text, std::wregex(L"[\u3000-\ua000]"))) {
									if (std::regex_search(text, std::wregex(L"[\u3000-\ua000]")))
									{
										hooks->push_back(std::wstring(hp.hookcode) + L"=>" + text + L"\n");

										//							*hooks << sanitize(S(HookCode::Generate(hp) + L" => " + text));
									}
								});
			}
			catch (wchar_t c)
			{
				std::wcout << c;
			}
			std::thread([hooks]
						{
					for (int lastSize = 0; hooks->size() == 0 || hooks->size() != lastSize; Sleep(2000)) lastSize = hooks->size();

					FILE* out = fopen("hook.txt", "a+,ccs=UTF-8");
					for (auto& hook : *hooks) {

						fwrite(hook.c_str(), wcslen(hook.c_str()) * sizeof(wchar_t), 1, out);
					}
					fclose(out); })
				.detach();
		}

		else
		{
			if (command[0] == L'-')
			{
				try
				{
					unsigned long long address;
					swscanf_s(command, L"-%llu", &address);
					Host::RemoveHook(processId, address);
				}
				catch (std::out_of_range)
				{
				}
			}
			else if (command[0] == L'=')
			{
				int codepage;
				swscanf_s(command, L"=%d", &codepage);
				Host::defaultCodepage = codepage;
			}
			else if (command[0] == L'+')
			{
				int flushDelay;
				swscanf_s(command, L"+%d", &flushDelay);
				TextThread::flushDelay = flushDelay;
			}
			else if (auto hp = HookCode::Parse(command))
				Host::InsertHook(processId, hp.value());
			else
				ExitProcess(0);
		}
	}
	ExitProcess(0);
}
