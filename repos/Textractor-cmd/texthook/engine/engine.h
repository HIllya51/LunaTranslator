#pragma once

// engine/engine.h
// 8/23/2013 jichi

#include <windows.h>

struct HookParam; // defined in ith types.h

extern uintptr_t processStartAddress, processStopAddress;

namespace Engine {

// Global variables
extern wchar_t *processName, // cached
               processPath[MAX_PATH]; // cached
inline const char *requestedEngine = nullptr, *loadedConfig = nullptr;

bool InsertMonoHooks(); // Mono

// Wii engines

bool InsertGCHooks(); // Dolphin
bool InsertVanillawareGCHook();

// PS2 engines

bool InsertPCSX2Hooks(); // PCSX2
bool InsertMarvelousPS2Hook();  // http://marvelous.jp
bool InsertMarvelous2PS2Hook(); // http://marvelous.jp
bool InsertTypeMoonPS2Hook();   // http://typemoon.com
//bool InsertNamcoPS2Hook();

// PSP engines

void SpecialPSPHook(DWORD esp_base, HookParam *hp, DWORD *data, DWORD *split, DWORD *len); // General PSP extern hook

bool FindPPSSPP();
bool InsertPPSSPPHooks();        // PPSSPPWindows

bool InsertPPSSPPHLEHooks();
bool InsertOtomatePPSSPPHook(); // PSP otomate.jp, 0.9.9.0 only

bool Insert5pbPSPHook();        // PSP 5pb.jp
bool InsertAlchemistPSPHook();  // PSP Alchemist-net.co.jp, 0.9.8 only
bool InsertAlchemist2PSPHook(); // PSP Alchemist-net.co.jp
bool InsertBandaiNamePSPHook(); // PSP Bandai.co.jp
bool InsertBandaiPSPHook();     // PSP Bandai.co.jp
bool InsertBroccoliPSPHook();   // PSP Broccoli.co.jp
bool InsertFelistellaPSPHook(); // PSP felistella.co.jp

bool InsertCyberfrontPSPHook(); // PSP CYBERFRONT (closed)
bool InsertImageepochPSPHook(); // PSP Imageepoch.co.jp
bool InsertImageepoch2PSPHook();// PSP Imageepoch.co.jp
bool InsertKadokawaNamePSPHook(); // PSP Kadokawa.co.jp
bool InsertKonamiPSPHook();     // PSP Konami.jp
bool InsertTecmoPSPHook();      // PSP Koeitecmo.co.jp
//bool InsertTypeMoonPSPHook(); // PSP Typemoon.com

bool InsertOtomatePSPHook();    // PSP Otomate.jp, 0.9.8 only
//bool InsertOtomate2PSPHook(); // PSP otomate.jp >= 0.9.9.1

bool InsertIntensePSPHook();    // PSP Intense.jp
bool InsertKidPSPHook();        // PSP Kid-game.co.jp
bool InsertNippon1PSPHook();    // PSP Nippon1.jp
bool InsertNippon2PSPHook();    // PSP Nippon1.jp
bool InsertYetiPSPHook();       // PSP Yetigame.jp
bool InsertYeti2PSPHook();      // PSP Yetigame.jp

// Game-speicific engines
bool InsertShinyDaysGameHook(); // ShinyDays
bool InsertLovaGameHook();      // lova.jp

// PC engines

bool Insert2RMHook();           // 2RM - Adventure Engine
bool Insert5pbHook();           // 5pb.jp, PSP/PS3 games ported to PC
bool InsertAB2TryHook();        // Yane@AkabeiSoft2Try: YaneSDK.dll.
bool InsertAbelHook();          // Abel
bool InsertAdobeAirHook();      // Adobe AIR
bool InsertAIRNovelHook();      // AIRNovel: *.swf
bool InsertAdobeFlash10Hook();  // Adobe Flash Player 10
bool InsertAliceHook();         // System40@AliceSoft; do not work for latest alice games
//bool InsertAmuseCraftHook();    // AMUSE CRAFT: *.pac
bool InsertAnex86Hook();        // Anex86: anex86.exe
bool InsertAOSHook();           // AOS: *.aos
bool InsertApricoTHook();       // Apricot: arc.a*
bool InsertArtemisHook();       // Artemis Engine: *.pfs
bool InsertAtelierHook();       // Atelier Kaguya: message.dat
bool InsertBGIHook();           // BGI: BGI.*
bool InsertBaldrHook();         // Baldr Sky "Zero"
bool InsertBootupHook();        // Bootup: Bootup.dat
bool InsertC4Hook();            // C4: C4.EXE or XEX.EXE
bool InsertCaramelBoxHook();    // Caramel: *.bin
bool InsertCandyHook();         // SystemC@CandySoft: *.fpk
bool InsertCatSystemHook();     // CatSystem2: *.int
bool InsertCMVSHook();          // CMVS: data/pack/*.cpz; do not support the latest cmvs32.exe and cmvs64.exe
bool InsertCotophaHook();       // Cotopha: *.noa
bool InsertDebonosuHook();      // Debonosu: bmp.bak and dsetup.dll
bool InsertEaglsHook();         // E.A.G.L.S: EAGLES.dll
bool InsertEMEHook();           // EmonEngine: emecfg.ecf
bool InsertEscudeHook();        // Escude
bool InsertEushullyHook();      // Eushully: AGERC.DLL
bool InsertExpHook();           // EXP: http://www.exp-inc.jp
bool InsertFocasLensHook();     // FocasLens: Dat/*.arc, http://www.fo-lens.net
bool InsertGXPHook();           // GXP: *.gxp
bool InsertHorkEyeHook();       // HorkEye: resource string
bool InsertKAGParserHook();     // plugin/KAGParser.dll
bool InsertKAGParserExHook();   // plugin/KAGParserEx.dll
bool InsertKiriKiriHook();      // KiriKiri: *.xp3, resource string
bool InsertKiriKiriZHook();     // KiriKiri: *.xp3, resource string
bool InsertLeafHook();          // Leaf: *.pak
bool InsertLiveHook();          // Live: live.dll
bool InsertLightvnHook();       // Light.vn: Engine.dll & BugTrapU.dll
bool InsertLunaSoftHook();      // LunaSoft: Pac/*.pac
bool InsertMalieHook();         // Malie@light: malie.ini
bool InsertMajiroHook();        // Majiro: *.arc
bool InsertMarineHeartHook();   // Marine Heart: SAISYS.exe
bool InsertMBLHook();           // MBL: *.mbl
bool InsertMEDHook();           // MED: *.med
bool InsertMinkHook();          // Mink: *.at2
//bool InsertMonoHook();          // Mono (Unity3D): */Mono/mono.dll
bool InsertNekopackHook();      // Nekopack: *.dat
bool InsertNeXASHook();         // NeXAS: Thumbnail.pac
bool InsertNextonHook();        // NEXTON: aInfo.db
bool InsertNexton1Hook();
bool InsertNitroplusHook();     // Nitroplus: *.npa
bool InsertTokyoNecroHook();    // Nitroplus TokyoNecro: *.npk, resource string
bool InsertPalHook();           // AMUSE CRAFT: *.pac
bool InsertPensilHook();        // Pensil: PSetup.exe
bool InsertPONScripterHook();
bool InsertQLIEHook();          // QLiE: GameData/*.pack
//bool InsertRai7Hook();          // Rai7puk: rai7.exe
bool InsertRejetHook();         // Rejet: Module/{gd.dat,pf.dat,sd.dat}
bool InsertRUGPHook();          // rUGP: rUGP.exe
bool InsertRenpyHook();         // Ren'py: python27.dll
bool InsertRetouchHook();       // Retouch: resident.dll
bool InsertRREHook();           // RunrunEngine: rrecfg.rcf
bool InsertShinaHook();         // ShinaRio: Rio.ini
bool InsertElfHook();           // elf: Silky.exe
bool InsertScenarioPlayerHook();// sol-fa-soft: *.iar && *.sec5
bool InsertSiglusHook();        // SiglusEngine: SiglusEngine.exe
bool InsertSideBHook();         // SideB: Copyright side-B
bool InsertSilkysHook();        // SilkysPlus
bool InsertSyuntadaHook();      // Syuntada: dSoh.dat
bool InsertSystem43Hook();      // System43@AliceSoft: AliceStart.ini
bool InsertSystemAoiHook();     // SystemAoi: *.vfs
bool InsertTamamoHook();        // Tamamo
bool InsertTanukiHook();        // Tanuki: *.tak
bool InsertTaskforce2Hook();    // Taskforce2.exe
bool InsertTencoHook();         // Tenco: Check.mdx
bool InsertTriangleHook();      // Triangle: Execle.exe
bool InsertV8Hook(HMODULE module); // V8 JavaScript runtime: has mangled v8::String::Write
bool InsertUnicornHook();       // Gsen18: *.szs|Data/*.szs
bool InsertWillPlusHook();      // WillPlus: Rio.arc
bool InsertWolfHook();          // Wolf: Data.wolf
bool InsertYukaSystem2Hook();   // YukaSystem2: *.ykc
bool InsertYurisHook();         // YU-RIS: *.ypf

void InsertBrunsHook();         // Bruns: bruns.exe
void InsertIronGameSystemHook();// IroneGameSystem: igs_sample.exe
void InsertLucifenHook();       // Lucifen@Navel: *.lpk
void InsertRyokuchaHook();      // Ryokucha: _checksum.exe
void InsertRealliveHook();      // RealLive: RealLive*.exe
void InsertStuffScriptHook();   // Stuff: *.mpk
bool InsertTinkerBellHook();    // TinkerBell: arc00.dat
bool InsertWaffleHook();        // WAFFLE: cg.pak

// CIRCUS: avdata/
bool InsertCircusHook1();
bool InsertCircusHook2();

} // namespace Engine

// EOF
