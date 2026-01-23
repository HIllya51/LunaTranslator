
uintptr_t &hook_context::argof(int idx, const HookParam *hp)
{
	return argof(idx, *hp);
}
uintptr_t &hook_context::argof(int idx, const HookParam &hp)
{
#ifndef _WIN64
	if ((hp.type & BREAK_POINT) && (idx >= 0))
	{
		return *((uintptr_t *)esp + idx);
	}
#endif
	return argof(idx);
}

uintptr_t &hook_context::offset(int offset, const HookParam *hp)
{
	return argof(offset, *hp);
}
uintptr_t &hook_context::offset(int offset, const HookParam &hp)
{
#ifndef _WIN64
	if ((hp.type & BREAK_POINT) && (offset >= 0))
	{
		return *(uintptr_t *)(esp + offset);
	}
#endif
	return *(uintptr_t *)(base + offset);
}
