#include <Psapi.h>

inline std::optional<std::wstring> GetModuleFilename(DWORD processId, HMODULE module = NULL)
{
	std::vector<wchar_t> buffer(MAX_PATH);
	if (AutoHandle<> process = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, FALSE, processId))
		if (GetModuleFileNameExW(process, module, buffer.data(), MAX_PATH)) return buffer.data();
	return {};
}

inline std::optional<std::wstring> GetModuleFilename(HMODULE module = NULL)
{
	std::vector<wchar_t> buffer(MAX_PATH);
	if (GetModuleFileNameW(module, buffer.data(), MAX_PATH)) return buffer.data();
	return {};
}

inline std::vector<std::pair<DWORD, std::optional<std::wstring>>> GetAllProcesses()
{
	std::vector<DWORD> processIds(10000);
	DWORD spaceUsed = 0;
	EnumProcesses(processIds.data(), 10000 * sizeof(DWORD), &spaceUsed);
	std::vector<std::pair<DWORD, std::optional<std::wstring>>> processes;
	for (int i = 0; i < spaceUsed / sizeof(DWORD); ++i) processes.push_back({ processIds[i], GetModuleFilename(processIds[i]) });
	return processes;
}
