include_directories(. util engines)
if(${CMAKE_SIZEOF_VOID_P} EQUAL 8) 
	set(enginessrc 
		BGI MKXPZ Ryujinx livecaptions Kincaid vita3k rpcs3 yuzu TYPEMOON UnrealEngine AGES7
		Godot 5pb lucasystem LightVN V8 Artemis KiriKiri YOX CMVS Suika2 GameMaker PCSX2
		Chunsoft)
	set(enginepath "engine64")
	set(collector "enginecollection64.cpp")
else()
	set(enginessrc 
		e_Erekiteru AbogadoPowers DAC BunBun antique T2U Moonstone Aromarie Winters Cage AGE_System 
		AksysGames RPGMaker Stronger TACTICS Onscripter Sceplay DISCOVERY Erogos godot A98SYS
		GuruGuruSMF4 TeethingRing Fizz CoffeeMaker VALKYRIA mirage CisLugI tamasoft FrontWing solfasys
		Diskdream splushwave ransel akatombo GASTRO GSX Aksys ScrPlayer SYSD KISS LucaSystem Jellyfish 
		BKEngine Overflow SRPGStudio Suika2 FVP LCScript Ohgetsu RPGMakerRGSS3 ONScripterru OVERDRIVE
		HXP Palette Purple Ruf RUNE Tarte Tomato Sakuradog Troy VitaminSoft UnknownEngine TSSystem
		Xbangbang Anisetta Nijyuei Interheart LovaGame Giga Jisatu101 EntisGLS Ciel ACTGS TerraLunar
		jukujojidai VanillawareGC cef V8 PONScripter Bishop sakanagl Lightvn KiriKiri SideB BGI
		Bootup morning shyakunage Regista NNNConfig Eushully Majiro littlecheese Elf Silkys CMVS Wolf
		Circus1 Circus2 Cotopha Artemis CatSystem Atelier Tenco QLIE Pal AIL NeXAS LunaSoft Unicorn
		Rejet Interlude AdobeAir Retouch Malie Live Nexton Lucifen Waffle TinkerBell SystemAoi Yuris
		Nitroplus2 Bruns EME RRE Candy Speed ApricoT Triangle AB2Try MBLMED GameMaker DxLib CodeX
		Minori Sprite RpgmXP Eagls Debonosu C4 WillPlus Tanuki GXP AOS Mink YukaSystem2 sakusesu Exp
		Syuntada Pensil Anim hibiki Nitroplus Reallive Siglus Taskforce2 RUGP IronGameSystem Anex86
		ShinyDaysGame MarineHeart ShinaRio CaramelBox UnisonShift Escude Ryokucha Alice Footy2
		utawarerumono System4x Abalone Abel 5pb HorkEye XUSE Leaf Nekopack AXL AGS AdobeFlash10
		FocasLens Tamamo Ages3ResT H_do_C RScript TYPEMOON TAKUYO MixwillSoft MerRouge GROOVER
		SmartAdv Hug GJ Pinpai)
	set(enginepath "engine32")
	set(collector "enginecollection32.cpp")
endif()
string(REPLACE ";" ".cpp;${enginepath}/" enginessrc "${enginessrc}")

set(enginessrc "${enginepath}/${enginessrc}.cpp")

set_source_files_properties(${enginessrc} PROPERTIES SOURCE_ENCODING "UTF-8")


add_library(pchhook pchhook.cpp)
target_precompile_headers(pchhook PUBLIC pchhook.h)


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

add_subdirectory(util)
add_subdirectory(engines)



add_library(LunaHook MODULE ${texthook_src} resource.rc ${versioninfo})

target_precompile_headers(LunaHook REUSE_FROM pchhook) 

set_target_properties(LunaHook PROPERTIES OUTPUT_NAME "LunaHook${bitappendix}")

target_link_libraries(LunaHook lang_hook VERSION_DEF Version httpapi ws2_32 Shlwapi pch minhook commonengine utils ${YY_Thunks})

target_link_options(LunaHook PRIVATE "/DELAYLOAD:httpapi.dll")
target_link_options(LunaHook PRIVATE "/DELAYLOAD:WS2_32.dll")
target_link_options(LunaHook PRIVATE "/DELAYLOAD:VERSION.dll")