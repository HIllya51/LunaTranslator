#pragma once

namespace HookCode
{
	std::optional<HookParam> Parse(std::wstring code);
	std::wstring Generate(HookParam hp, DWORD processId = 0);
}
