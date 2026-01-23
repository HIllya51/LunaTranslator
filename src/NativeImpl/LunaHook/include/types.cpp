
uintptr_t &hook_context::smart_argof(int idx, const HookParam *hp)
{
	return smart_argof(idx, *hp);
}
uintptr_t &hook_context::smart_argof(int idx, const HookParam &hp)
{
#ifndef _WIN64
	if ((hp.type & BREAK_POINT) && (idx >= 0))
	{
		return *((uintptr_t *)esp + idx);
	}
#endif
	return argof(idx);
}

uintptr_t &hook_context::smart_offset(int offset, const HookParam *hp)
{
	return smart_argof(offset, *hp);
}
uintptr_t &hook_context::smart_offset(int offset, const HookParam &hp)
{
#ifndef _WIN64
	if ((hp.type & BREAK_POINT) && (offset >= 0))
	{
		return *(uintptr_t *)(esp + offset);
	}
#endif
	return *(uintptr_t *)(base + offset);
}
