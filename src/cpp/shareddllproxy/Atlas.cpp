#include "Atlas.h"
// https://github.com/uyjulian/AtlasTranslate

wchar_t AtlasPath[2 * MAX_PATH];
static int atlasVersion = 0;

int GetAtlasVersion()
{
	return atlasVersion;
}

static int atlasTransDirection = 0;

int GetAtlasTransDirection()
{
	return atlasTransDirection;
}

// dir is 1 for jap to eng, 2 for eng to jap.
typedef int __cdecl CreateEngineType(int x, int dir, int x3, char *x4);
static CreateEngineType *CreateEngine = 0;

typedef int __cdecl DestroyEngineType();
static DestroyEngineType *DestroyEngine = 0;

typedef int __cdecl TranslatePairType(char *in, char **out, void **dunno, unsigned int *maybeSize);
static TranslatePairType *TranslatePair = 0;

typedef int __cdecl AtlInitEngineDataType(int x1, int x2, int *x3, int x4, int *x5);
static AtlInitEngineDataType *AtlInitEngineData = 0;

// No clue what this does.  Doesn't set direction.
typedef int __cdecl SetTransStateType(int dunno);
static SetTransStateType *SetTransState = 0;

static FreeAtlasDataType *FreeAtlasData = 0;
AwuWordDelType *AwuWordDel = 0;

// static TextRuleSet *ruleSet = 0;

// typedef int __cdecl AwuDlgAtlasPopupEnvDetailSetType(void *, char *type, void *x3, char *word);
// AwuDlgAtlasPopupEnvDetailSetType *AwuDlgAtlasPopupEnvDetailSet = 0;

HMODULE atlecont = 0;
HMODULE awdict = 0;
HMODULE awuenv = 0;
int atlasHappy = 0;

void UninitAtlas()
{
	atlasTransDirection = 0;
	atlasVersion = 0;
	if (atlasHappy)
	{
		DestroyEngine();
		atlasHappy = 0;
	}
	// if (ruleSet)
	// {
	// 	delete ruleSet;
	// 	ruleSet = 0;
	// }

	if (atlecont)
	{
		FreeLibrary(atlecont);
		atlecont = 0;
	}
	if (awdict)
	{
		FreeLibrary(awdict);
		awdict = 0;
	}
	if (awuenv)
	{
		FreeLibrary(awuenv);
		awuenv = 0;
	}
}

// ATLAS_CAN_MODIFY lets me modify the original string, otherwise
// make and use a copy.
// ATLAS_NO_FREE means to return the atlas results directly
// rather than copy them over to a standard malloc-ed string.
char *AtlasTransSJIS(char *jis, int flags)
{
	// Don't bother removing extra bytes, since it doesn't last long.
	char *outjis = 0;
	void *unsure = 0;
	unsigned int maybeSize = 0;
	char *temp = jis;
	if (!(flags & ATLAS_CAN_MODIFY))
		temp = (char *)malloc(1 + strlen(jis));
	int p1 = 0;
	int p2 = 0;
	int lastJis = 1;
	while (jis[p1])
	{
		if (jis[p1] == ' ' || jis[p1] == '\t' || jis[p1] == '\n' || jis[p1] == '\r' ||
			(jis[p1] == -127 && jis[p1 + 1] == 64))
		{
			if (jis[p1] == -127)
				p1++;
			p1++;
			if (!lastJis)
				temp[p2++] = ' ';
		}
		else
		{
			lastJis = (jis[p1] < 0 && ((unsigned char)jis[p1] != 0x82 || (unsigned char)jis[p1 + 1] >= 0x9E || jis[p1 + 1] < 0x4F));
			if (lastJis)
				while (p2 > 0 && temp[p2 - 1] == ' ')
					p2--;
			unsigned char u = jis[p1];
			// double-byte JIS.
			if ((u >= 0x81 && u <= 0x9F) ||
				(u >= 0xE0 && u <= 0xEF))
				temp[p2++] = jis[p1++];
			temp[p2++] = jis[p1++];
		}
	}
	temp[p2] = 0;
	// I completely ignore res.  Not sure if it matters.
	int res = TranslatePair(temp, &outjis, &unsure, &maybeSize);
	if (!(flags & ATLAS_CAN_MODIFY))
		free(temp);

	if (unsure)
		FreeAtlasData(unsure, 0, 0, 0);
	if ((flags & ATLAS_NO_FREE))
		return outjis;
	if (outjis)
	{
		char *out = strdup(outjis);
		FreeAtlasData(outjis, 0, 0, 0);
		return out;
	}
	return 0;
}

wchar_t *AtlasTrans(const wchar_t *text, int len)
{
	// return original string if no Japanese characters.
	// if (atlasTransDirection == ATLAS_JAP_TO_ENG && !HasJap(text)) return 0;
	// Don't bother removing extra bytes, since it doesn't last long.
	if (len < 0)
		len = (int)wcslen(text);
	int len2 = 4 * len + 1;
	char *jis = (char *)malloc(len2);
	len2 = WideCharToMultiByte(932, 0, text, -1, jis, len2, 0, 0);
	char *outjis;
	if (!len2 || !(outjis = AtlasTransSJIS(jis, ATLAS_CAN_MODIFY | ATLAS_NO_FREE)))
	{
		free(jis);
		return 0;
	}
	free(jis);

	// Extra is so I can add on punctuation if I want.
	len2 = (int)(3 + strlen(outjis));
	wchar_t *out = (wchar_t *)malloc(sizeof(wchar_t) * len2);
	len2 = (int)MultiByteToWideChar(932, 0, outjis, -1, out, len2);
	FreeAtlasData(outjis, 0, 0, 0);
	if (len2)
		return out;
	free(out);
	return 0;
}

int LoadAtlasDlls()
{
	if (atlecont && awdict && awuenv)
		return 1;
	wchar_t newPath[MAX_PATH * 2];
	for (int i = 0; i < 2; i++)
	{
		for (int v = 14; v >= 13; v--)
		{
			if (i == 0)
			{
				wchar_t temp[MAX_PATH];
				wsprintfW(temp, L"Software\\Fujitsu\\ATLAS\\V%i.0\\EJ", v);
				HKEY hKey = 0;
				if (ERROR_SUCCESS != RegOpenKey(HKEY_CURRENT_USER, temp, &hKey))
					continue;
				DWORD type;
				DWORD size = sizeof(newPath) - 2;
				wchar_t *name;
				int res = RegQueryValueExW(hKey, L"TRENV EJ", 0, &type, (BYTE *)newPath, &size);
				RegCloseKey(hKey);
				if (ERROR_SUCCESS != res || type != REG_SZ || !(name = wcsrchr(newPath, '\\')))
					continue;
				name[1] = 0;
			}
#ifndef NO_SHELL32
			else
			{
				if (S_OK != SHGetFolderPathW(0, CSIDL_PROGRAM_FILES, 0, SHGFP_TYPE_CURRENT, newPath))
					continue;
				wsprintfW(wcschr(newPath, 0), L"\\ATLAS V%i\\", v);
			}
#endif
			wchar_t *w = wcschr(newPath, 0);
			wcscpy(w, L"AtleCont.dll");
			atlecont = LoadLibraryEx(newPath, 0, LOAD_WITH_ALTERED_SEARCH_PATH);
			wcscpy(w, L"awdict.dll");
			awdict = LoadLibraryEx(newPath, 0, LOAD_WITH_ALTERED_SEARCH_PATH);
			wcscpy(w, L"awuenv.dll");
			awuenv = LoadLibraryEx(newPath, 0, LOAD_WITH_ALTERED_SEARCH_PATH);
			if (atlecont && awdict && awuenv)
			{
				*w = 0;
				wcscpy(AtlasPath, newPath);
				atlasVersion = v;
				return 1;
			}
			UninitAtlas();
		}
	}
	return 0;
}

int AtlasIsLoaded()
{
	return atlasHappy;
}

int InitAtlas(AtlasConfig &cfg, int transDirection)
{
	if (atlasHappy)
	{
		if (transDirection == atlasTransDirection)
			return 1;
		UninitAtlas();
	}
	if (!LoadAtlasDlls())
		return 0;
	if (atlecont && awdict &&
		(CreateEngine = (CreateEngineType *)GetProcAddress(atlecont, "CreateEngine")) &&
		(DestroyEngine = (DestroyEngineType *)GetProcAddress(atlecont, "DestroyEngine")) &&
		(TranslatePair = (TranslatePairType *)GetProcAddress(atlecont, "TranslatePair")) &&
		(FreeAtlasData = (FreeAtlasDataType *)GetProcAddress(atlecont, "FreeAtlasData")) &&
		(AtlInitEngineData = (AtlInitEngineDataType *)GetProcAddress(atlecont, "AtlInitEngineData")) &&
		(SetTransState = (SetTransStateType *)GetProcAddress(atlecont, "SetTransState")) &&
		//(AwuDlgAtlasPopupEnvDetailSet = (AwuDlgAtlasPopupEnvDetailSetType*)(awuenv, "AwuDlgAtlasPopupEnvDetailSet")) &&
		(AwuWordDel = (AwuWordDelType *)GetProcAddress(awdict, "AwuWordDel")))
	{
		union
		{
			char temp[MAX_PATH * 4];
			wchar_t path[MAX_PATH * 2];
		};
		wcscpy(path, cfg.trsPath);
		wchar_t *name = wcsrchr(path, '\\');
		if (name)
		{
			name[0] = 0;
			name++;
		}
		else
		{
			name = cfg.trsPath;
			wcscpy(path, L"Rule Sets\\");
		}
		if (1)
		{
			if (WideCharToMultiByte(932, 0, cfg.environment, -1, temp, 4 * MAX_PATH, 0, 0))
			{
				// SetTransState(1);
				// Needed?  No clue.
				static int dunno[1000] = {0};
				static int dunno2[1000] = {0};
				if (0 == AtlInitEngineData(0, 2, dunno, 0, dunno2) && 1 == CreateEngine(1, transDirection, 0, temp))
				{
					atlasTransDirection = transDirection;
					atlasHappy = 1;
					return 1;
					//}
				}
			}
		}
	}
	UninitAtlas();
	return 0;
}

// Basically just AtlasThreadProc, with some stuff removed.
wchar_t *TranslateFull(wchar_t *otext, int freeText, int NeedAbort(int line, int lines, void *data), void *data)
{
	if (!otext) //|| !ruleSet)
		return 0;

	if (!otext)
		return 0;
	int len1 = wcslen(otext);
	auto needFree = AtlasTrans(otext, len1);
	return needFree;

	int memLen = wcslen(otext);
	int len = memLen;
	int count = 1;
	wchar_t *snipped = otext; // ruleSet->ParseText(otext, &len, &count);
	wchar_t *text = otext;
	if (!freeText)
		text = (wchar_t *)malloc(sizeof(wchar_t) * memLen);
	text[0] = 0;
	len = 0;
	int pos = 0;

	// Doesn't work, sadly.  Looks like atlas isn't threadsafe.
	/*
	wchar_t **strings = (wchar_t**) malloc(sizeof(wchar_t*) * count);
	wchar_t *p = snipped;
	for (int i=0; i<count; i++)
	{
		strings[i] = p;
		while (*p) p++;
		p++;
		while (*p) p++;
		p++;
	}
	int needExit = 0;
#pragma omp parallel for schedule(dynamic,1)
	for (int i=0; i<count; i++)
	{
		if (needExit) continue;
		if (NeedAbort && NeedAbort(i, count, data))
		{
			needExit = 1;
			continue;
		}
		wchar_t *trans = wcschr(strings[i], 0) + 1;
		wchar_t *needFree = AtlasTrans(trans, wcslen(trans));
		if (needFree)
			free(needFree);
	}
	free(strings);
	//*/

	for (int i = 0; i < count; i++)
	{
		if (NeedAbort && NeedAbort(i, count, data))
			break;
		wchar_t *trans, *prefix;
		prefix = snipped + pos;
		trans = wcschr(prefix, 0) + 1;
		pos = (int)((wcschr(trans, 0) + 1) - snipped);

		int oldLen = len;
		wchar_t *needFree = 0;
		if (trans[0])
		{
			int len1 = wcslen(trans);
			needFree = AtlasTrans(trans, len1);
			if (needFree)
			{
				trans = needFree;
				// Copy over ending punctuation if it ATLAS got it wrong.
				// Note:  Commas currently handled elsewhere.
				int len2 = wcslen(needFree);
				if (len1 > 0 && len2 > 1)
				{
					wchar_t e1 = trans[len1 - 1];
					wchar_t *e2 = &needFree[len2];
					if (e2[-1] == ' ')
						e2--;
					if (e2[-1] == '.' || e2[-1] == ',' || e2[-1] == '?' || e2[-1] == '!')
						e2--;
					// desired punctuation.
					wchar_t p = 0;
					if (e1 == L'！')
						p = '!';
					if (e1 == L'？')
						p = '!';
					if (e1 == L'。')
						p = '.';
					if (p)
					{
						if (*e2 == L'.' || *e2 == L'?' || *e2 == L'!')
						{
							// First part of handling for "!?" and shouted questions without '?'.
							// second part further down.
							if (*e2 == '?')
							{
								if (e1 == L'！')
									wcscpy(e2, L"!? ");
							}
							else if (*e2 == '.')
								*e2 = p;
						}
						else
						{
							e2[0] = p;
							e2[1] = ' ';
							e2[2] = 0;
						}
					}
				}
			}
			len += wcslen(trans);
		}
		len += wcslen(prefix);

		if (len + 20 >= memLen)
		{
			memLen = len + len / 2 + 1000;
			text = (wchar_t *)realloc(text, sizeof(wchar_t) * memLen);
		}
		if (prefix)
		{
			if (prefix[0] == ',')
			{
				if (oldLen && text[oldLen - 1] == ' ')
					oldLen--;
				if (oldLen && text[oldLen - 1] == '.' || text[oldLen - 1] == ',')
					oldLen--;
			}
			else if (prefix[0] == '.')
			{
				if (oldLen && text[oldLen - 1] == ' ')
					oldLen--;
				if (oldLen > 1 && text[oldLen - 1] == '.' && (text[oldLen - 2] == '.' || prefix[0] == '.'))
					oldLen--;
				// Fix !...,  ?..., and ?...?
				if (oldLen && (text[oldLen - 1] == '?' || text[oldLen - 1] == '!'))
				{
					int s = oldLen - 1;
					while (s && text[s - 1] == '!' || text[s - 1] == '?')
						s--;
					int count1 = oldLen - s;
					int count2 = 1;
					while (prefix[count2] == '.')
						count2++;
					memmove(text + oldLen + count2 - count1, text + s, (count1 + 1) * sizeof(wchar_t));
					memcpy(text + s, prefix, sizeof(wchar_t) * count2);
					prefix += count2;
					oldLen += count2;
					// handle the extra ? in ?...?
					if (prefix[0] == text[oldLen - 1])
						prefix++;
				}
			}
			else if (prefix[0] == '?' || prefix[0] == '!')
			{
				if (oldLen && text[oldLen - 1] == ' ')
					oldLen--;
				if (oldLen > 1 && text[oldLen - 1] == '?')
					if (oldLen > 2 && text[oldLen - 2] == '!')
						oldLen--;
			}
			wcscpy(text + oldLen, prefix);
			oldLen += wcslen(prefix);
		}
		if (trans)
		{
			if (oldLen && (text[oldLen - 1] == ',' || text[oldLen - 1] == '.' || text[oldLen - 1] == '!' || text[oldLen - 1] == '?'))
				text[oldLen++] = ' ';
			if (oldLen > 1 && (text[oldLen - 2] == '.' || text[oldLen - 2] == '!' || text[oldLen - 2] == '?'))
				text[oldLen++] = ' ';
			wcscpy(text + oldLen, trans);
			oldLen += wcslen(trans);
		}
		len = oldLen;

		if (needFree)
			free(needFree);
	}
	free(snipped);
	if (len && text[len - 1] == ' ')
		text[len - 1] = 0;
	return text;
}

char *TranslateFull(char *otext, int freeText, int NeedAbort(int line, int lines, void *data), void *data)
{
	int len = -1;
	auto ws = StringToWideString(otext, 932);
	if (!ws.size())
		return 0;
	wchar_t *outw = TranslateFull(ws.data(), freeText, NeedAbort, data);

	if (!outw)
		return 0;
	len = -1;
	auto s = WideStringToString(outw, 932);
	char *out = new char[s.size() + 1];
	strcpy(out, s.c_str());
	free(outw);
	return out;
}

struct AtlasConfig atlcfg;

void writestring(const wchar_t *text, HANDLE hPipe);
wchar_t *readstring(HANDLE hPipe);
int atlaswmain(int argc, wchar_t *argv[])
{

	HANDLE hPipe = CreateNamedPipe(argv[1], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

	SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[2]));
	if (!ConnectNamedPipe(hPipe, NULL))
		return 0;
	while (true)
	{
		wchar_t *src = readstring(hPipe);
		if (!src)
			break;

		if (!AtlasIsLoaded())
		{
			// atlcfg.flags = ~BREAK_ON_SINGLE_LINE_BREAKS;
			wcscpy(atlcfg.environment, L"Entertainment");
			wcscpy(atlcfg.trsPath, L"");
			InitAtlas(atlcfg, ATLAS_JAP_TO_ENG);
			if (!AtlasIsLoaded())
			{
				writestring(0, hPipe);
				return false;
			}
		}
		wchar_t *text = TranslateFull(src, 0, NULL, NULL);
		writestring(text, hPipe);
		free(src);
		free(text);
	}

	return 0;
}