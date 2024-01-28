cmake_minimum_required(VERSION 3.5.2)

#
#  VC-LTL自动化加载配置，建议你将此文件单独复制到你的工程再使用，该文件能自动识别当前环境是否存在VC-LTL，并且自动应用。
#
#  使用方法：
#    1. 在“CMakeLists.txt” 添加 “include("VC-LTL helper for cmake.cmake")”。
#
#  VC-LTL默认搜索顺序
#    1. “VC-LTL helper for cmake.cmake”所在根目录，即 ${CMAKE_CURRENT_LIST_DIR}
#    2. 当前CMake根目录，即 ${CMAKE_CURRENT_SOURCE_DIR}/VC-LTL
#    3. 当前项目根目录，即 ${PROJECT_SOURCE_DIR}/VC-LTL
#    4. 当前CMake父目录，即 ${CMAKE_CURRENT_SOURCE_DIR}/../VC-LTL
#    5. 当前项目根目录，即 ${PROJECT_SOURCE_DIR}/../VC-LTL
#    6. 注册表HKEY_CURRENT_USER\Code\VC-LTL@Root
#
#  把VC-LTL放在其中一个位置即可，VC-LTL就能被自动引用。
# 
#  如果你对默认搜索顺序不满，你可以修改此文件。你也可以直接指定${VC_LTL_Root}宏更加任性的去加载VC-LTL。
#




#####################################################################VC-LTL设置#####################################################################

#控制TargetPlatform版本，目前可用版本为5.1.2600.0     6.0.6000.0（默认）    6.2.9200.0     10.0.10240.0    10.0.19041.0
#set(WindowsTargetPlatformMinVersion "10.0.10240.0")

#启用干净的导入表，消除 ucrt apiset(如：api-ms-win-crt-time-l1-1-0.dll)，满足强迫症患者。
#set(CleanImport "true")

####################################################################################################################################################

if(NOT VC_LTL_Root)
	if(EXISTS ${CMAKE_CURRENT_LIST_DIR}/_msvcrt.h)
		set(VC_LTL_Root ${CMAKE_CURRENT_LIST_DIR})
	endif()
endif()

if(NOT VC_LTL_Root)
	if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/VC-LTL/_msvcrt.h)
		set(VC_LTL_Root ${CMAKE_CURRENT_SOURCE_DIR}/VC-LTL)
	endif()
endif()

if(NOT VC_LTL_Root)
	if(EXISTS ${PROJECT_SOURCE_DIR}/VC-LTL/_msvcrt.h)
        set(VC_LTL_Root ${PROJECT_SOURCE_DIR}/VC-LTL)
    endif()
endif()

if(NOT VC_LTL_Root)
	if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/../VC-LTL/_msvcrt.h)
        set(VC_LTL_Root ${CMAKE_CURRENT_SOURCE_DIR}/../VC-LTL)
    endif()
endif()

if(NOT VC_LTL_Root)
	if(EXISTS ${PROJECT_SOURCE_DIR}/../VC-LTL/_msvcrt.h)
        set(VC_LTL_Root ${PROJECT_SOURCE_DIR}/../VC-LTL)
    endif()
endif()

if(NOT VC_LTL_Root)
    EXECUTE_PROCESS(COMMAND reg query "HKEY_CURRENT_USER\\Code\\VC-LTL" -v "Root"
                    OUTPUT_VARIABLE FOUND_FILE 
                    ERROR_VARIABLE ERROR_INFO
                   )

    string(REGEX MATCH "[a-zA-Z]:\\\\.+\\\\" 
           FOUND_LTL 
           ${FOUND_FILE})
    if (NOT ${FOUND_LTL} STREQUAL "")
        set(VC_LTL_Root ${FOUND_LTL})
    endif()

    if(NOT DEFINED VC_LTL_Root) 
        string(REGEX MATCH "\\\\\\\\.+\\\\" FOUND_LTL ${FOUND_FILE})
        if (NOT ${FOUND_LTL} STREQUAL "")
            set(VC_LTL_Root ${FOUND_LTL})
        endif()
    endif()
endif()

if(VC_LTL_Root)
    include("${VC_LTL_Root}\\config\\config.cmake")
endif()
