#pragma once

#define ATLAS_JAP_TO_ENG 1
#define ATLAS_ENG_TO_JAP 2

// returns 0 if not initialized.
int GetAtlasTransDirection();

// Keep internal copy of flags and loaded rule set,
// which I cleanup on uninit.
struct AtlasConfig
{
	unsigned int flags;
	wchar_t environment[MAX_PATH];
	wchar_t trsPath[MAX_PATH];
};

int InitAtlas(AtlasConfig &cfg, int transDirection);
void UninitAtlas();
int GetAtlasVersion();

typedef int __cdecl FreeAtlasDataType(void *mem, void *noSureHowManyArgs, void *, void *);
// extern FreeAtlasDataType *FreeAtlasData;

// Opens up dictionary type.  Think word is what word to open it at, but the "Del" makes me wary.
typedef int __cdecl AwuWordDelType(int x1, char *type, int x3, char *word);
extern AwuWordDelType *AwuWordDel;

#define ATLAS_CAN_MODIFY 1
#define ATLAS_NO_FREE 2

// canModify means don't need to duplicate jis input string.
char *AtlasTransSJIS(char *jis, int flags = 0);
wchar_t *AtlasTrans(const wchar_t *jap, int len = -1);
extern wchar_t AtlasPath[2 * MAX_PATH];
int LoadAtlasDlls();
wchar_t *TranslateFull(wchar_t *otext, int freeText = 0, int NeedAbort(int line, int lines, void *data) = 0, void *data = 0);
char *TranslateFull(char *otext, int freeText = 0, int NeedAbort(int line, int lines, void *data) = 0, void *data = 0);

int AtlasIsLoaded();

/*
wchar_t path[MAX_PATH];
GetCurrentDirectory(MAX_PATH, path);
delete LoadRuleSet(path, L"default.trs");
//*/
