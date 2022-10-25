// match.cc
// 8/9/2013 jichi
// Branch: ITH_Engine/engine.cpp, revision 133

#include "engine/match.h"
#include "engine/engine.h"
#include "engine/native/pchooks.h"
#include "util/util.h"
#include "main.h"
#include "ithsys/ithsys.h"

//#define ConsoleOutput(...)  (void)0     // jichi 8/18/2013: I don't need ConsoleOutput

enum { MAX_REL_ADDR = 0x200000 }; // jichi 8/18/2013: maximum relative address

// - Methods -

namespace Engine { namespace { // unnamed

bool DetermineGameHooks() // 7/19/2015
{
#if 0 // jichi 7/19/2015: Disabled as it will crash the game
  if (Util::CheckFile(L"UE3ShaderCompileWorker.exe") && Util::CheckFile(L"awesomium_process.exe")) {
    InsertLovaGameHook();
    return true;
  }
#endif // 0
  return false;
}

// jichi 7/17/2014: Disable GDI hooks for PPSSPP
bool DeterminePCEngine()
{
  if (DetermineGameHooks()) {
    ConsoleOutput("vnreng: found game-specific hook");
    return true;
  }

  //if (Util::CheckFile(L"PPSSPP*.exe")) { // jichi 7/12/2014 PPSSPPWindows.exe, PPSSPPEX.exe PPSSPPSP.exe
  //  //InsertPPSSPPHooks(); // Artikash 8/4/2018: removed for now as doesn't work for non ancient ppsspp versions
	 // FindPPSSPP();
  //  return true;
  //}

  if (Util::CheckFile(L"PPSSPP*.exe") && FindPPSSPP()) return true;

  if (Util::CheckFile(L"pcsx2*.exe")) { // jichi 7/19/2014 PCSX2.exe or PCSX2WX.exe
    InsertPCSX2Hooks();
    return true;
  }

  if (Util::CheckFile(L"Dolphin.exe")) { // jichi 7/20/2014
    InsertGCHooks();
    return true;
  }

  // jichi 5/14/2015: Skip hijacking BALDRSKY ZEROs
  //if (Util::CheckFile(L"bsz_Data\\Mono\\mono.dll") || Util::CheckFile(L"bsz2_Data\\Mono\\mono.dll")) {
  //  ConsoleOutput("vnreng: IGNORE BALDRSKY ZEROs");
  //  return true;
  //}

  for (std::wstring DXVersion : { L"d3dx9", L"d3dx10" })
	  if (HMODULE module = GetModuleHandleW(DXVersion.c_str())) PcHooks::hookD3DXFunctions(module);
	  else for (int i = 0; i < 50; ++i)
		  if (HMODULE module = GetModuleHandleW((DXVersion + L"_" + std::to_wstring(i)).c_str())) PcHooks::hookD3DXFunctions(module);

  for (HMODULE module : { (HMODULE)processStartAddress, GetModuleHandleW(L"node.dll"), GetModuleHandleW(L"nw.dll") })
	  if (GetProcAddress(module, "?Write@String@v8@@QBEHPAGHHH@Z")) return InsertV8Hook(module);

  if (InsertMonoHooks()) {
    return true;
  }

  if (GetModuleHandleW(L"GameAssembly.dll")) // TODO: is there a way to autofind hook?
  {
      ConsoleOutput("Textractor: Precompiled Unity found (searching for hooks should work)");
      wcscpy_s(spDefault.boundaryModule, L"GameAssembly.dll");
      spDefault.padding = 12;
      return true;
  }

  // PC games
  PcHooks::hookGDIFunctions();
  PcHooks::hookGDIPlusFunctions();
  return false;
}

bool DetermineEngineByFile1()
{
	if (Util::SearchResourceString(L"Proportional ONScripter") || Util::SearchResourceString(L"ponscr.exe"))
	{
		InsertPONScripterHook();
		return true;
	}
  // Artikash 7/14/2018: AIRNovel - sample game https://vndb.org/v18814
  if (Util::CheckFile(L"*.swf"))
  {
	  //InsertAdobeAirHook();
	InsertAIRNovelHook();
	return true;
  }

  // Artikash 8/9/2018: Renpy - sample game https://vndb.org/v19843
  if (Util::CheckFile(L"*.py"))
  {
	  InsertRenpyHook();
	  return true;
  }

  if (GetModuleHandleW(L"Engine.dll") && GetModuleHandleW(L"BugTrapU.dll"))
  {
	  InsertLightvnHook();
	  return true;
  }

  if (Util::CheckFile(L"*.xp3") || Util::SearchResourceString(L"TVP(KIRIKIRI)")) {
    if (Util::SearchResourceString(L"TVP(KIRIKIRI) Z ")) { // TVP(KIRIKIRI) Z CORE
      // jichi 11/24/2014: Disabled that might crash VBH
      //if (Util::CheckFile(L"plugin\\KAGParser.dll"))
      //  InsertKAGParserHook();
      //else if (Util::CheckFile(L"plugin\\KAGParserEx.dll"))
      //  InsertKAGParserExHook();
      if (InsertKiriKiriZHook())
        return true;
    }
    InsertKiriKiriHook();
    return true;
  }
  // 8/2/2014 jichi: Game name shown as 2RM - Adventure Engine, text also in GetGlyphOutlineA
  if (Util::SearchResourceString(L"2RM") && Util::SearchResourceString(L"Adventure Engine")) {
    Insert2RMHook();
    return true;
  }
  // 8/2/2014 jichi: Copyright is side-B, a conf.dat will be generated after the game is launched
  // It also contains lua5.1.dll and lua5.dll
  if (Util::SearchResourceString(L"side-B")) {
    InsertSideBHook();
    return true;
  }
  if (Util::CheckFile(L"bgi.*") || Util::CheckFile(L"sysgrp.arc")) {
    InsertBGIHook();
    return true;
  }
  if (Util::CheckFile(L"Bootup.dat") && InsertBootupHook()) // 5/22/2015 Bootup
    // lstrlenW can also find text with repetition though
    return true;
  if (Util::CheckFile(L"AGERC.DLL")) { // 6/1/2014 jichi: Eushully, AGE.EXE
    InsertEushullyHook();
    return true;
  }
  if (Util::CheckFile(L"data*.arc") && Util::CheckFile(L"stream*.arc")) {
    InsertMajiroHook();
    return true;
  }
  // jichi 5/31/2014
  if (//Util::CheckFile(L"Silkys.exe") ||    // It might or might not have Silkys.exe
      // data, effect, layer, mes, music
      Util::CheckFile(L"data.arc") && Util::CheckFile(L"effect.arc") && Util::CheckFile(L"mes.arc")) {
    InsertElfHook();
    return true;
  }
  // jichi 6/9/2015: Skip Silkys Sakura
  if ( // Almost the same as Silkys except mes.arc is replaced by Script.arc
      Util::CheckFile(L"data.arc") && Util::CheckFile(L"effect.arc") && Util::CheckFile(L"Script.arc")) {
    InsertSilkysHook();
    return true;
  }
  if (Util::CheckFile(L"data\\pack\\*.cpz")) {
    InsertCMVSHook();
    return true;
  }
  // jichi 10/12/2013: Restore wolf engine
  // jichi 10/18/2013: Check for data/*.wolf
  if (Util::CheckFile(L"data.wolf") || Util::CheckFile(L"data\\*.wolf") || Util::CheckFile(L"data\\basicdata\\cdatabase.dat")) {
    InsertWolfHook();
    return true;
  }
  if (Util::CheckFile(L"AdvData\\DAT\\NAMES.DAT")) {
    InsertCircusHook1();
    return true;
  }
  if (Util::CheckFile(L"AdvData\\GRP\\NAMES.DAT")) {
    InsertCircusHook2();
    return true;
  }
  if (Util::CheckFile(L"*.noa") || Util::CheckFile(L"data\\*.noa")) {
    InsertCotophaHook();
    return true;
  }
  if (Util::CheckFile(L"*.pfs")) { // jichi 10/1/2013
    InsertArtemisHook();
    return true;
  }
  if (Util::CheckFile(L"*.int") && InsertCatSystemHook()) {
    return true;
  }
  if (Util::CheckFile(L"message.dat")) {
    InsertAtelierHook();
    return true;
  }
  if (Util::CheckFile(L"Check.mdx")) { // jichi 4/1/2014: AUGame
    InsertTencoHook();
    return true;
  }
  // jichi 12/25/2013: It may or may not be QLIE.
  // AlterEgo also has GameData/sound.pack but is not QLIE
  if (Util::CheckFile(L"GameData\\*.pack") && InsertQLIEHook())
    return true;

  if (Util::CheckFile(L"dll\\Pal.dll")) {
    InsertPalHook();
    return true;
  }

  if (Util::CheckFile(L"*.pac")) {
    // jichi 6/3/2014: AMUSE CRAFT and SOFTPAL
    // Selectively insert, so that lstrlenA can still get correct text if failed
    //if (Util::CheckFile(L"dll\\resource.dll") && Util::CheckFile(L"dll\\pal.dll") && InsertAmuseCraftHook())
    //  return true;

    if (Util::CheckFile(L"Thumbnail.pac")) {
      //ConsoleOutput("vnreng: IGNORE NeXAS");
      InsertNeXASHook(); // jichi 7/6/2014: GIGA
      return true;
    }

    if (Util::SearchResourceString(L"SOFTPAL")) {
      ConsoleOutput("vnreng: IGNORE SoftPal UNiSONSHIFT");
      return true;
    }
  }
  // jichi 12/27/2014: LunaSoft
  if (Util::CheckFile(L"Pac\\*.pac")) {
    InsertLunaSoftHook();
    return true;
  }
  // jichi 9/16/2013: Add Gesen18
  if (Util::CheckFile(L"*.szs") || Util::CheckFile(L"Data\\*.szs")) {
    InsertUnicornHook();
    return true;
  }
  // jichi 12/22/2013: Add rejet
  if (Util::CheckFile(L"gd.dat") && Util::CheckFile(L"pf.dat") && Util::CheckFile(L"sd.dat")) {
    InsertRejetHook();
    return true;
  }
  // Only examined with version 1.0
  //if (Util::CheckFile(L"Adobe AIR\\Versions\\*\\Adobe AIR.dll")) { // jichi 4/15/2014: FIXME: Wildcard not working
  if (Util::CheckFile(L"Adobe AIR\\Versions\\1.0\\Adobe AIR.dll")) { // jichi 4/15/2014: Adobe AIR
    InsertAdobeAirHook();
    return true;
  }
  return false;
}

bool DetermineEngineByFile2()
{
  if (Util::CheckFile(L"resident.dll")) {
    InsertRetouchHook();
    return true;
  }
  if (Util::CheckFile(L"Malie.ini") || Util::CheckFile(L"Malie.exe")) { // jichi: 9/9/2014: Add malie.exe in case malie.ini is missing
    InsertMalieHook();
    return true;
  }
  if (Util::CheckFile(L"live.dll")) {
    InsertLiveHook();
    return true;
  }
  // 9/5/2013 jichi
  if (Util::CheckFile(L"aInfo.db")) {
    InsertNextonHook();
    return true;
  }
  if (Util::CheckFile(L"*.lpk")) {
    InsertLucifenHook();
    return true;
  }
  if (Util::CheckFile(L"cfg.pak")) {
    InsertWaffleHook();
    return true;
  }
  if (Util::CheckFile(L"Arc00.dat") && InsertTinkerBellHook()) {
    return true;
  }
  if (Util::CheckFile(L"*.vfs")) { // jichi 7/6/2014: Better to test AoiLib.dll? ja.wikipedia.org/wiki/ソフトハウスキャラ
    InsertSystemAoiHook();
    return true;
  }
  if (Util::CheckFile(L"*.mbl")) {
    InsertMBLHook();
    return true;
  }
  // jichi 8/1/2014: YU-RIS engine, lots of clockup game also has this pattern
  if (Util::CheckFile(L"pac\\*.ypf") || Util::CheckFile(L"*.ypf")) {
    // jichi 8/14/2013: CLOCLUP: "ノーブレスオブリージュ" would crash the game.
    if (!Util::CheckFile(L"noblesse.exe"))
      InsertYurisHook();
    return true;
  }
  if (Util::CheckFile(L"*.npa")) {
    InsertNitroplusHook();
    return true;
  }
  return false;
}

bool DetermineEngineByFile3()
{
  //if (Util::CheckFile(L"libscr.dll")) { // already checked
  //  InsertBrunsHook();
  //  return true;
  //}

  // jichi 10/12/2013: Sample args.txt:
  // See: http://tieba.baidu.com/p/2631413816
  // -workdir
  // .
  // -loadpath
  // .
  // am.cfg
  if (Util::CheckFile(L"args.txt")) {
    InsertBrunsHook();
    return true;
  }
  if (Util::CheckFile(L"emecfg.ecf")) {
    InsertEMEHook();
    return true;
  }
  if (Util::CheckFile(L"rrecfg.rcf")) {
    InsertRREHook();
    return true;
  }
  if (Util::CheckFile(L"*.fpk") || Util::CheckFile(L"data\\*.fpk")) {
    InsertCandyHook();
    return true;
  }
  if (Util::CheckFile(L"arc.a*")) {
    InsertApricoTHook();
    return true;
  }
  if (Util::CheckFile(L"*.mpk")) {
    InsertStuffScriptHook();
    return true;
  }
  if (Util::CheckFile(L"USRDIR\\*.mpk")) { // jichi 12/2/2014
    InsertStuffScriptHook();
    return true;
  }
  if (Util::CheckFile(L"Execle.exe")) {
    InsertTriangleHook();
    return true;
  }
  // jichi 2/28/2015: No longer work for "大正×対称アリス episode I" from Primula
  //if (Util::CheckFile(L"PSetup.exe")) {
  //  InsertPensilHook();
  //  return true;
  //}
  if (Util::CheckFile(L"Yanesdk.dll")) {
    InsertAB2TryHook();
    return true;
  }
  if (Util::CheckFile(L"*.med")) {
    InsertMEDHook();
    return true;
  }
  return false;
}

bool DetermineEngineByFile4()
{
  if (Util::CheckFile(L"EAGLS.dll")) { // jichi 3/24/2014: E.A.G.L.S
    //ConsoleOutput("vnreng: IGNORE EAGLS");
    InsertEaglsHook();
    return true;
  }
  if (Util::CheckFile(L"bmp.pak") && Util::CheckFile(L"dsetup.dll")) {
    // 1/1/2016 jich: skip izumo4 from studio ego that is not supported by debonosu
    if (Util::CheckFile(L"*izumo4*.exe")) {
      PcHooks::hookOtherPcFunctions();
      return true;
    }
    InsertDebonosuHook();
    return true;
  }
  if (Util::CheckFile(L"C4.EXE") || Util::CheckFile(L"XEX.EXE")) {
    InsertC4Hook();
    return true;
  }
  if (Util::CheckFile(L"Rio.arc") && Util::CheckFile(L"Chip*.arc")) {
    InsertWillPlusHook();
    return true;
  }
  if (Util::CheckFile(L"*.tac")) {
    InsertTanukiHook();
    return true;
  }
  if (Util::CheckFile(L"*.gxp")) {
    InsertGXPHook();
    return true;
  }
  if (Util::CheckFile(L"*.aos")) { // jichi 4/2/2014: AOS hook
    InsertAOSHook();
    return true;
  }
  if (Util::CheckFile(L"*.at2")) { // jichi 12/23/2014: Mink, sample files: voice.at2, voice.det, voice.nme
    InsertMinkHook();
    return true;
  }
  if (Util::CheckFile(L"*.ykc")) { // jichi 7/15/2014: YukaSystem1 is not supported, though
    //ConsoleOutput("vnreng: IGNORE YKC:Feng/HookSoft(SMEE)");
    InsertYukaSystem2Hook();
    return true;
  }
  if (Util::CheckFile(L"model\\*.hed")) { // jichi 9/8/2014: EXP
    InsertExpHook();
    return true;
  }
  // jichi 2/6/2015 平安亭
  // dPi.dat, dPih.dat, dSc.dat, dSch.dat, dSo.dat, dSoh.dat, dSy.dat
  //if (Util::CheckFile(L"dSoh.dat")) { // no idea why this file does not work
  if (Util::CheckFile(L"dSch.dat")) {
    InsertSyuntadaHook();
    return true;
  }

  // jichi 2/28/2015: Delay checking Pensil in case something went wrong
  // File pattern observed in [Primula] 大正×対称アリス episode I
  // - PSetup.exe no longer exists
  // - MovieTexture.dll information shows MovieTex dynamic library, copyright Pensil 2013
  // - ta_trial.exe information shows 2XT - Primula Adventure Engine
  if (Util::CheckFile(L"PSetup.exe") || Util::CheckFile(L"PENCIL.*") || Util::SearchResourceString(L"2XT -")) {
    InsertPensilHook();
    return true;
  }

  // jichi 11/22/2015: 凍京NECRO 体験版
  // Jazzinghen 23/05/2020: Add check for 凍京NECRO
  // ResEdit shows multiple potential strings:
  // - TOKYONECRO
  // - 東京NECRO
  // - TokyoNecro.exe in "OriginalFilename"
  if (Util::CheckFile(L"*.npk")) {
    if (Util::SearchResourceString(L"TOKYONECRO")) {
      InsertTokyoNecroHook();
    }
    else {
      ConsoleOutput("vnreng: IGNORE new Nitroplus");
    }
    return true;
  }

  return false;
}

bool DetermineEngineByProcessName()
{
  WCHAR str[MAX_PATH];
  wcscpy_s(str, processName);
  _wcslwr_s(str); // lower case

  if (wcsstr(str,L"reallive") || Util::CheckFile(L"Reallive.exe") || Util::CheckFile(L"REALLIVEDATA\\Start.ini")) {
    InsertRealliveHook();
    return true;
  }

  // jichi 8/19/2013: DO NOT WORK for games like「ハピメア」
  //if (wcsstr(str,L"cmvs32") || wcsstr(str,L"cmvs64")) {
  //  InsertCMVSHook();
  //  return true;
  //}

  // jichi 8/17/2013: Handle "~"
  if (wcsstr(str, L"siglusengine") || !wcsncmp(str, L"siglus~", 7) || Util::CheckFile(L"SiglusEngine.exe")) {
    InsertSiglusHook();
    return true;
  }

  if (wcsstr(str, L"taskforce2") || !wcsncmp(str, L"taskfo~", 7) || Util::CheckFile(L"Taskforce2.exe")) {
    InsertTaskforce2Hook();
    return true;
  }

  if (wcsstr(str,L"rugp") || Util::CheckFile(L"rugp.exe")) {
    InsertRUGPHook();
    return true;
  }

  // jichi 8/17/2013: Handle "~"
  if (wcsstr(str, L"igs_sample") || !wcsncmp(str, L"igs_sa~", 7) || Util::CheckFile(L"igs_sample.exe")) {
    InsertIronGameSystemHook();
    return true;
  }

  if (wcsstr(str, L"bruns") || Util::CheckFile(L"bruns.exe")) {
    InsertBrunsHook();
    return true;
  }

  if (wcsstr(str, L"anex86") || Util::CheckFile(L"anex86.exe")) {
    InsertAnex86Hook();
    return true;
  }

  // jichi 8/17/2013: Handle "~"
  if (wcsstr(str, L"shinydays") || !wcsncmp(str, L"shinyd~", 7) || Util::CheckFile(L"ShinyDays.exe")) {
    InsertShinyDaysGameHook();
    return true;
  }

  if (wcsstr(processName, L"SAISYS") || Util::CheckFile(L"SaiSys.exe")) { // jichi 4/19/2014: Marine Heart
    InsertMarineHeartHook();
    return true;
  }

  DWORD len = wcslen(str);

  // jichi 8/24/2013: Checking for Rio.ini or $procname.ini
  //wcscpy(str+len-4, L"_?.war");
  //if (Util::CheckFile(str)) {
  //  InsertShinaHook();
  //  return true;
  //}
  if (Util::CheckFile(L"*.ini")) {
	if (InsertShinaHook())
      return true;
  }

  // jichi 8/10/2013: Since *.bin is common, move CaramelBox to the end
  str[len - 3] = L'b';
  str[len - 2] = L'i';
  str[len - 1] = L'n';
  str[len] = 0;
  if ((Util::CheckFile(str) || Util::CheckFile(L"trial.bin")) // jichi 7/8/2014: add trial.bin
      && InsertCaramelBoxHook())
    return true;

  // jichi 7/23/2015  It also has gameexe.bin existed
  if (Util::CheckFile(L"configure.cfg") && Util::CheckFile(L"gfx.bin")) {
    InsertEscudeHook();
    return true;
  }

  // This must appear at last since str is modified
  //wcscpy(str + len - 4, L"_checksum.exe");
  if (Util::CheckFile(L"*_checksum.exe")) {
    InsertRyokuchaHook();

    if (Util::CheckFile(L"*.iar") && Util::CheckFile(L"*.sec5")) // jichi 9/27/2014: For new Ryokucha games
      InsertScenarioPlayerHook();
    return true;
  }

  return false;
}

bool DetermineEngineOther()
{
  if (InsertAliceHook())
    return true;
  // jichi 1/19/2015: Disable inserting Lstr for System40
  // See: http://sakuradite.com/topic/618
  if (Util::CheckFile(L"System40.ini")) {
    ConsoleOutput("vnreng: IGNORE old System40.ini");
    return true;
  }
  // jichi 12/26/2013: Add this after alicehook
  if (Util::CheckFile(L"AliceStart.ini")) {
    InsertSystem43Hook();
    return true;
  }

  // Artikash 7/16/2018: Uses node/libuv: likely v8 - sample game https://vndb.org/v22975
  //if (GetProcAddress(GetModuleHandleW(nullptr), "uv_uptime") || GetModuleHandleW(L"node.dll"))
  //{
	 // InsertV8Hook();
	 // return true;
  //}

  // jichi 8/24/2013: Move into functions
  // Artikash 6/15/2018: Removed this detection for Abel Software games. IthGetFileInfo no longer works correctly
  //static BYTE static_file_info[0x1000];
  //if (IthGetFileInfo(L"*01", static_file_info))
  //  if (*(DWORD*)static_file_info == 0) {
  //    STATUS_INFO_LENGTH_MISMATCH;
  //    static WCHAR static_search_name[MAX_PATH];
  //    LPWSTR name=(LPWSTR)(static_file_info+0x5E);
  //    int len = wcslen(name);
  //    name[len-2] = L'.';
  //    name[len-1] = L'e';
  //    name[len] = L'x';
  //    name[len+1] = L'e';
  //    name[len+2] = 0;
  //    if (Util::CheckFile(name)) {
		//  sizeof(FILE_BOTH_DIR_INFORMATION);
  //      name[len-2] = L'*';
  //      name[len-1] = 0;
  //      wcscpy(static_search_name,name);
  //      IthGetFileInfo(static_search_name,static_file_info);
  //      union {
  //        FILE_BOTH_DIR_INFORMATION *both_info;
  //        DWORD addr;
  //      };
  //      both_info = (FILE_BOTH_DIR_INFORMATION *)static_file_info;
  //      //BYTE* ptr=static_file_info;
  //      len=0;
  //      while (both_info->NextEntryOffset) {
  //        addr += both_info->NextEntryOffset;
  //        len++;
  //      }
  //      if (len > 3) {
  //        InsertAbelHook();
  //        return true;
  //      }
  //    }
  //  }

  return false;
}

// jichi 8/17/2014
// Put the patterns that might break other games at last
bool DetermineEngineAtLast()
{
	if (Util::CheckFile(L"*.g2")) {
		InsertTanukiHook();
		return true;
	}
  if (Util::CheckFile(L"MovieTexture.dll") && (InsertPensilHook() || Insert2RMHook())) // MovieTexture.dll also exists in 2RM games such as 母子愛2体験版, which is checked first
    return true;
  if ((Util::CheckFile(L"system") && Util::CheckFile(L"system.dat")) || Util::CheckFile(L"*01")) // jichi 7/31/2015 & Artikash 6/15/2018
    if (InsertAbelHook())
      return true;
  if (Util::CheckFile(L"data\\*.cpk")) { // jichi 12/2/2014
    Insert5pbHook();
    return true;
  }
  // jichi 7/6/2014: named as ScenarioPlayer since resource string could be: scenario player program for xxx
  // Do this at last as it is common
  if (Util::CheckFile(L"*.iar") && Util::CheckFile(L"*.sec5")) { // jichi 4/18/2014: Other game engine could also have *.iar such as Ryokucha
    InsertScenarioPlayerHook();
    return true;
  }
  //if (Util::CheckFile(L"arc0.dat") && Util::CheckFile(L"script.dat") // jichi 11/14/2014: too common
  if (Util::SearchResourceString(L"HorkEye")) { // appear in copyright: Copyright (C) HorkEye, http://horkeye.com
    InsertHorkEyeHook();
    return true;
  }
  if (Util::CheckFile(L"comnArc.arc") // jichi 8/17/2014: this file might exist in multiple files
      && InsertNexton1Hook()) // old nexton game
    return true;
  if (Util::CheckFile(L"arc.dat") // jichi 9/27/2014: too common
      && InsertApricoTHook())
    return true;
  if (Util::CheckFile(L"*.pak") // jichi 12/25/2014: too common
      && InsertLeafHook())
    return true;
  if (Util::CheckFile(L"*.dat") // mireado 08/22/2016: too common
      && InsertNekopackHook())
    return true;
  // jichi 10/31/2014
  // File description: Adobe Flash Player 10.2r153
  // Product name: Shockwave Flash
  // Original filename: SAFlashPlayer.exe
  // Legal trademarks: Adobe Flash Player
  // No idea why, this must appear at last or it will crash
  if (Util::SearchResourceString(L"Adobe Flash Player 10")) {
    InsertAdobeFlash10Hook(); // only v10 might be supported. Otherwise, fallback to Lstr hooks
    return true;
  }
  if (Util::CheckFile(L"dat\\*.arc")) { // jichi 2/6/2015
    InsertFocasLensHook(); // Touhou
    return true;
  }

  // jichi 8/23/2015: Tamamo
  if (Util::CheckFile(L"data.pck") && Util::CheckFile(L"image.pck") && Util::CheckFile(L"script.pck")) {
    //if (Util::CheckFile(L"QtGui.dll"))
    InsertTamamoHook();
    return true;
  }

  return false;
}

// jichi 6/1/2014
// Artikash 9/3/2018 Hook wchar by default
//bool DetermineEngineGeneric()
//{
//  bool ret = false;
//
//  //if (Util::CheckFile(L"AlterEgo.exe")) {
//  //  ConsoleOutput("vnreng: AlterEgo, INSERT WideChar hooks");
//  //  ret = true;
//  //}  else if (Util::CheckFile(L"data\\Sky\\*")) {
//  //  ConsoleOutput("vnreng: TEATIME, INSERT WideChar hooks");
//  //  ret = true;
//  //}
//  ////}  else if (Util::CheckFile(L"image\\*.po2") || Util::CheckFile(L"image\\*.jo2")) {
//  ////  ConsoleOutput("vnreng: HarukaKanata, INSERT WideChar hooks"); // はるかかなた
//  ////  ret = true;
//  ////}
//  //if (ret)
//  //  PcHooks::hookWcharFunctions();
//  PcHooks::hookWcharFunctions();
//  return ret;
//}

bool DetermineNoEngine()
{
  //if (Util::CheckFile(L"*\\Managed\\UnityEngine.dll")) { // jichi 12/3/2013: Unity (BALDRSKY ZERO)
  //  ConsoleOutput("vnreng: IGNORE Unity");
  //  return true;
  //}
  //if (Util::CheckFile(L"bsz_Data\\Managed\\UnityEngine.dll") || Util::CheckFile(L"bsz2_Data\\Managed\\UnityEngine.dll")) {
  //  ConsoleOutput("vnreng: IGNORE Unity");
  //  return true;
  //}

  // jichi 6/7/2015: RPGMaker v3
  if (Util::CheckFile(L"*.rgss3a")) {
    ConsoleOutput("vnreng: IGNORE RPGMaker RGSS3");
    return true;
  }

  // 8/29/2015 jichi: minori, text in GetGlyphOutlineA
  if (Util::CheckFile(L"*.paz")) {
    ConsoleOutput("vnreng: IGNORE minori");
    return true;
  }

  // 7/28/2015 jichi: Favorite games
  if (Util::CheckFile(L"*.hcb")) {
    ConsoleOutput("vnreng: IGNORE FVP");
    return true;
  }

  // jichi 2/14/2015: Guilty+ ＲＩＮ×ＳＥＮ (PK)
  if (/*Util::CheckFile(L"rio.ini") || */Util::CheckFile(L"*.war")) {
    ConsoleOutput("vnreng: IGNORE unknown ShinaRio");
    return true;
  }

  if (Util::CheckFile(L"AdvHD.exe") || Util::CheckFile(L"AdvHD.dll")) {
    ConsoleOutput("vnreng: IGNORE Adv Player HD"); // supposed to be WillPlus
    return true;
  }

  if (Util::CheckFile(L"ScrPlayer.exe")) {
    ConsoleOutput("vnreng: IGNORE ScrPlayer");
    return true;
  }

  if (Util::CheckFile(L"nnnConfig2.exe")) {
    ConsoleOutput("vnreng: IGNORE Nya NNNConfig");
    return true;
  }

  // jichi 4/30/2015: Skip games made from らすこう, such as とある人妻のネトラレ事情
  // It has garbage from lstrlenW. Correct text is supposed to be in TabbedTextOutA.
  if (Util::CheckFile(L"data_cg.dpm")) {
    ConsoleOutput("vnreng: IGNORE DPM data_cg.dpm");
    return true;
  }

  //if (Util::CheckFile(L"AGERC.DLL")) { // jichi 3/17/2014: Eushully, AGE.EXE
  //  ConsoleOutput("vnreng: IGNORE Eushully");
  //  return true;
  //}

  if (Util::CheckFile(L"game_sys.exe")) {
    ConsoleOutput("vnreng: IGNORE Atelier Kaguya BY/TH");
    return true;
  }

  if (Util::CheckFile(L"*.bsa")) {
    ConsoleOutput("vnreng: IGNORE Bishop");
    return true;
  }

  // jichi 3/19/2014: Escude game
  // Example: bgm.bin gfx.bin maou.bin script.bin snd.bin voc.bin
  if (Util::CheckFile(L"gfx.bin") && Util::CheckFile(L"snd.bin") && Util::CheckFile(L"voc.bin")) {
    ConsoleOutput("vnreng: IGNORE Escude");
    return true;
  }

  // jichi 2/18/2015: Ignore if there is Nitro+ copyright
  if (Util::SearchResourceString(L"Nitro+")) {
    ConsoleOutput("vnreng: IGNORE unknown Nitro+");
    return true;
  }

  // jichi 12/28/2014: "Chartreux Inc." in Copyright.
  // Sublimary brands include Rosebleu, MORE, etc.
  // GetGlyphOutlineA already works.
  if (Util::SearchResourceString(L"Chartreux")) {
    ConsoleOutput("vnreng: IGNORE Chartreux");
    return true;
  }

  if (Util::CheckFile(L"MovieTexture.dll")) {
    ConsoleOutput("vnreng: IGNORE MovieTexture");
    return true;
  }

  if (wcsstr(processName, L"lcsebody") || !wcsncmp(processName, L"lcsebo~", 7) || Util::CheckFile(L"lcsebody*")) { // jichi 3/19/2014: LC-ScriptEngine, GetGlyphOutlineA
    ConsoleOutput("vnreng: IGNORE lcsebody");
    return true;
  }

  wchar_t str[MAX_PATH];
  DWORD i;
  for (i = 0; processName[i]; i++) {
    str[i] = processName[i];
    if (processName[i] == L'.')
      break;
  }
  *(DWORD *)(str + i + 1) = 0x630068; //.hcb
  *(DWORD *)(str + i + 3) = 0x62;
  if (Util::CheckFile(str)) {
    ConsoleOutput("vnreng: IGNORE FVP"); // jichi 10/3/2013: such like アトリエかぐや
    return true;
  }
  return false;
}

} // unnamed

// jichi 9/14/2013: Certain ITH functions like FindEntryAligned might raise exception without admin priv
// Return if succeeded.
bool UnsafeDetermineEngineType()
{
  return DeterminePCEngine()
    || DetermineEngineByFile1()
    || DetermineEngineByFile2()
    || DetermineEngineByFile3()
    || DetermineEngineByFile4()
    || DetermineEngineByProcessName()
    || DetermineEngineOther()
    || DetermineEngineAtLast()
    || DetermineNoEngine()
  ;
}

} // namespace Engine

// - API -

// EOF
