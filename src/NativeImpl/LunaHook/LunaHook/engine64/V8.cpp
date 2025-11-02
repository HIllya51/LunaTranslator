#include "V8.h"
#include "v8/v8.h"
#if 0
// Artikash 6/23/2019: V8 (JavaScript runtime) has rcx = string** at v8::String::Write
// sample game https://www.freem.ne.jp/dl/win/18963
bool InsertV8Hook(HMODULE module)
{
	uint64_t addr1 = (uint64_t)GetProcAddress(module, "?Write@String@v8@@QEBAHPEAGHHH@Z"),
		// Artikash 6/7/2021: Add new hook for new version of V8 used by RPG Maker MZ
		addr2 = (uint64_t)GetProcAddress(module, "??$WriteToFlat@G@String@internal@v8@@SAXV012@PEAGHH@Z");

	if (addr1 || addr2)
	{
		std::tie(spDefault.minAddress, spDefault.maxAddress) = Util::QueryModuleLimits(module);
		spDefault.maxRecords = Util::SearchMemory(spDefault.pattern, spDefault.length, PAGE_EXECUTE, spDefault.minAddress, spDefault.maxAddress).size() * 20;
		ConsoleOutput("JavaScript hook is known to be low quality: try searching for hooks if you don't like it");
	}
	auto succ=false;
	if (addr1)
	{
		HookParam hp;
		hp.type = USING_STRING | CODEC_UTF16;
		hp.address = addr1;
		hp.text_fun = [](hook_context *context, HookParam *hp, uintptr_t* data, uintptr_t* split, size_t* count)
		{
			*data=(*(uintptr_t*)(context->rcx))+23;
			int len = *(int*)(*data - 4);
			if(wcslen((wchar_t*)*data)*2<len)return;
			*count=len*2;
		};
		succ|=NewHook(hp, "JavaScript");
	}
	if (addr2)
	{
		HookParam hp;
		hp.type = USING_STRING | CODEC_UTF16;
		hp.address = addr2;
		hp.text_fun = [](hook_context *context, HookParam *hp, uintptr_t* data, uintptr_t* split, size_t* count)
		{
			*data=(context->rcx)+11;
			int len = *(int*)(*data - 4);
			if(wcslen((wchar_t*)*data)*2<len)return;
			*count=len*2;
		};
		succ|=NewHook(hp, "JavaScript");
	}
	return succ;
}
namespace{
	uintptr_t forwardsearch(BYTE* b,int size,uintptr_t addr,int range){
		for(int i=0;i<range;i++){
			bool ok=true;
			for(int j=0;j<size;j++){
				if((*(BYTE*)(b+j))==XX)continue;
				if((*(BYTE*)(b+j))!=((*(BYTE*)(addr+i+j)))){
					ok=false;break;
				}
			}
			if(ok){
				return addr+i;
			}
		}
		return 0;
	}
	regs andregimm(BYTE* b){
		 
		if(*b==0x81)
			switch (*(b+1))
			{
			case 0xe1:return regs::rcx;//rcx
			case 0xe2:return regs::rdx;//rdx
			case 0xe3:return regs::rbp;//rbx
			case 0xe5:return regs::rbp;//rbp
			case 0xe6:return regs::rsi;//rsi
			case 0xe7:return regs::rdi;//rdi
			default:return regs::invalid;
			}
		else  
			return regs::invalid;
	}
	std::vector<HookParam> hookw(HMODULE module){
		const BYTE BYTES[] = {
				0x81,XX,0x00,0xf8,0x00,0x00
		};
		std::vector<HookParam>save;
		auto addrs = Util::SearchMemory(BYTES, sizeof(BYTES), PAGE_EXECUTE, processStartAddress, processStopAddress);
		for(auto addr:addrs){
			auto addrsave=addr;
			BYTE sig1[]={0x81,XX,0x00,0xD8,0x00,0x00};
			BYTE sig2[]={0x81,XX,0x00,0xFC,0x00,0x00};
			BYTE sig3[]={0x81,XX,0x00,0xDC,0x00,0x00};
			BYTE sig4[]={XX,0x00,0x24,0xA0,0xFC};

			addr=forwardsearch(sig1,sizeof(sig1),addr,0x20);
			if(!addr)continue;
			
			addr=forwardsearch(sig2,sizeof(sig2),addr,0x100);
			if(!addr)continue;
			
			addr=forwardsearch(sig3,sizeof(sig3),addr,0x20);
			if(!addr)continue;
			
			addr=forwardsearch(sig4,sizeof(sig4),addr,0x20);
			if(!addr)continue;
			auto off=andregimm((BYTE*)addrsave);
			if(off==regs::invalid)continue;
			HookParam hp;
			hp.address = (uint64_t)addrsave ;
			hp.type =  CODEC_UTF16|NO_CONTEXT ;
			hp.offset =get_reg(off);
			save.push_back(hp);
			
		}
		return save;
	}
#if 0
	std::vector<HookParam> v8hook1(HMODULE module) {
		
		const BYTE BYTES[] = {
				0x81,0xE1,0x00,0xF8,0x00,0x00,
				0x41,0xBE,0x01,0x00,0x00,0x00,
				0x81,0xF9,0x00,0xD8,0x00,0x00
		};
		auto addrs = Util::SearchMemory(BYTES, sizeof(BYTES), PAGE_EXECUTE, processStartAddress, processStopAddress);
		if (addrs.size() != 1)return {};
		auto addr = (uint64_t)addrs[0];
		const BYTE start[] = {
				0xCC
		};
		const BYTE start2[] = {
				0x41,0x57,0x41,0x56,0x41,0x55,0x41,0x54
		};
		addr=reverseFindBytes(start, sizeof(start), addr - 0x1000, addr);
		if (!addr)return {};
		addr += 1; 
		addrs = findxref_reverse(addr, addr - 0x10000, addr + 0x10000);
		if (addrs.size() != 1)return {};
		addr = addrs[0]; 
		
		addr = reverseFindBytes(start2, sizeof(start2), addr - 0x1000, addr);
		if (!addr)return {};
		addrs = findxref_reverse(addr, addr - 0x10000, addr + 0x10000);
		std::vector<HookParam> save;
		for (auto addr : addrs) {
			addr = reverseFindBytes(start2, sizeof(start2), addr - 0x1000, addr);
			if (!addr)continue;
			HookParam hp;
			hp.address = (uint64_t)addr;
			hp.type = USING_STRING | CODEC_UTF16 | DATA_INDIRECT;
			hp.offset=regoffset(rcx);
			hp.padding = 0xC;
			hp.index = 0;
				
			save.push_back(hp);
		}
		return save;
	}
#endif
	bool innerHTML(HMODULE module) {
		//花葬
		//result = sub_142DF3CA0(a2, v5, 1u, (__int64)"innerHTML", a3);
		//r10当全为ascii是普通string，否则为wchar_t
		//a3是一个callback,并不是字符串。
		char innerHTML[]="innerHTML";
		auto addr = MemDbg::findBytes(innerHTML, sizeof(innerHTML),  processStartAddress, processStopAddress);
		ConsoleOutput("%x",addr);
		if(!addr)return false;
		bool ok=false;
		for(auto _addr=processStartAddress+4;_addr<processStopAddress;_addr+=1){
			if((_addr+*(int*)(_addr-4) )==addr){
				ConsoleOutput("%x",_addr-processStartAddress);
				for(int i=0;i<0x20;i++){
					if(*(BYTE*)(_addr+i)==0xe8){
						uintptr_t subaddr=_addr+i+5+*(int*)(_addr+i+1);
						HookParam hp;
						hp.address = (uint64_t)subaddr;
						hp.type = USING_STRING | CODEC_UTF16 ;
						hp.offset=regoffset(r10);
						hp.text_fun=[](hook_context *context, HookParam* hp, uintptr_t* data, uintptr_t* split, size_t* len){
							auto text =context->r10;
							if(strlen((char*) text)>1){
								hp->type=USING_STRING|CODEC_UTF8|NO_CONTEXT;
								*split=0x1;
								*len=strrchr((char*)text,'>')+1-(char*)text;
							}
							else{
								hp->type=USING_STRING|CODEC_UTF16|NO_CONTEXT;
								*split=0x10;
								*len=wcsrchr((wchar_t*)text,L'>')+1-(wchar_t*)text;
								*len*=2;
							}
						};
						ok|=NewHook(hp,"innerHTML");
					}
				}
			}
		}
		return ok;
	}
	bool addhooks(HMODULE module){
		if (GetProcAddress(module, "?Write@String@v8@@QEBAHPEAVIsolate@2@PEAGHHH@Z") == 0)return false;
		bool success=false;
		for(auto h:hookw(module)){
			success|=NewHook(h,"electronW");
		}
		return innerHTML(module)|| success;
	}
}

#endif
bool V8::attach_function_()
{

	return tryhookv8();
}
