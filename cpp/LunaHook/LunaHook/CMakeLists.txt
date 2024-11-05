include_directories(. util engines)
if(${CMAKE_SIZEOF_VOID_P} EQUAL 8) 
	set(enginessrc MKXPZ Ryujinx livecaptions Kincaid vita3k rpcs3 yuzu TYPEMOON UnrealEngine AGES7 mono Godot 5pb lucasystem LightVN V8 pchooks Artemis KiriKiri YOX PPSSPP CMVS Suika2 )
	set(enginepath "engine64")
	set(collector "enginecollection64.cpp")
else()
	set(enginessrc Cage AGE_System AksysGames RPGMaker Stronger TACTICS Onscripter Sceplay DISCOVERY Erogos godot A98SYS GuruGuruSMF4 TeethingRing Fizz CoffeeMaker VALKYRIA mirage CisLugI tamasoft FrontWing solfasys Diskdream splushwave ransel akatombo GASTRO GSX Aksys ScrPlayer SYSD KISS IGScript Jellyfish BKEngine Overflow SRPGStudio Suika2 FVP LCScript Ohgetsu RPGMakerRGSS3 ONScripterru OVERDRIVE HXP Palette Purple Ruf RUNE Tarte Tomato Sakuradog Troy VitaminSoft UnknownEngine TSSystem Xbangbang Anisetta Nijyuei Interheart LovaGame Giga Jisatu101 EntisGLS Ciel ACTGS TerraLunar PPSSPP jukujojidai PCSX2 VanillawareGC cef V8 mono pchooks PONScripter Bishop sakanagl Lightvn KiriKiri SideB BGI Bootup morning shyakunage Regista NNNConfig Eushully Majiro littlecheese Elf Silkys CMVS Wolf Circus1 Circus2 Cotopha Artemis CatSystem Atelier Tenco QLIE Pal AIL2 NeXAS LunaSoft Unicorn Rejet Interlude AdobeAir Retouch Malie Live Nexton Lucifen Waffle TinkerBell SystemAoi Yuris Nitroplus2 Bruns EME RRE Candy Speed ApricoT Triangle AB2Try MBLMED GameMaker DxLib CodeX Minori Sprite RpgmXP Eagls Debonosu C4 WillPlus Tanuki GXP AOS Mink YukaSystem2 sakusesu Exp Syuntada Pensil Anim hibiki Nitroplus Reallive Siglus Taskforce2 RUGP IronGameSystem Anex86 ShinyDaysGame MarineHeart ShinaRio CaramelBox UnisonShift Escude Ryokucha Alice Footy2 utawarerumono System4x Abalone Abel 5pb HorkEye XUSE Leaf Nekopack AXL AGS AdobeFlash10 FocasLens Tamamo Ages3ResT)
	set(enginepath "engine32")
	set(collector "enginecollection32.cpp")
endif()
string(REPLACE ";" ".cpp;${enginepath}/" enginessrc "${enginessrc}")
#message("${enginessrc}")
set(enginessrc "${enginepath}/${enginessrc}.cpp")
message("${enginessrc}")
set_source_files_properties(${enginessrc} PROPERTIES SOURCE_ENCODING "UTF-8")

set(texthook_src
		main.cc
		texthook.cc
		hookfinder.cc
		${enginessrc}
		${collector}
		enginecontrol.cpp
		embed_util.cc
		hijackfuns.cc
		veh_hook.cpp
) 


add_library(pchhook pchhook.cpp)
target_precompile_headers(pchhook PUBLIC pchhook.h)


add_subdirectory(util)
add_subdirectory(engines)

generate_product_version(
   versioninfohook
   NAME "LunaHook"
   COMPANY_COPYRIGHT "HIllya51 (C) 2024"
   ICON ${PATH_TO_APPLICATION_ICON}
   VERSION_MAJOR ${VERSION_MAJOR}
   VERSION_MINOR ${VERSION_MINOR}
   VERSION_PATCH ${VERSION_PATCH}
   VERSION_REVISION ${VERSION_REVISION}
)

add_library(LunaHook MODULE ${texthook_src} resource.rc ${versioninfohook})

target_precompile_headers(LunaHook REUSE_FROM pchhook) 

set_target_properties(LunaHook PROPERTIES OUTPUT_NAME "LunaHook${bitappendix}")

target_link_libraries(LunaHook Version httpapi ws2_32 Shlwapi pch minhook commonengine utils ${YY_Thunks_for_WinXP})