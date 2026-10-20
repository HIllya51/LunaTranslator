
include(FetchContent)

#https://github.com/ikegami-yukino/mecab clone太几把慢了
FetchContent_Declare(mecab
    GIT_REPOSITORY https://github.com/HIllya51/mecab
    GIT_TAG master
    GIT_SHALLOW TRUE
)
FetchContent_Populate(mecab)

set(mecabsrc "${mecab_SOURCE_DIR}/mecab/src")

function(remove_register_from_files root_dir)
    file(GLOB_RECURSE all_files 
        LIST_DIRECTORIES false
        "${root_dir}/*.cpp"
        "${root_dir}/*.h"
    )
    
    foreach(file_path IN LISTS all_files)
        file(READ "${file_path}" file_content)
        
        string(FIND "${file_content}" "register" position)
        if(NOT position EQUAL -1)
            string(REPLACE
                "register" 
                "" 
                new_content 
                "${file_content}"
            )
            if(NOT "${file_content}" STREQUAL "${new_content}")
                file(WRITE "${file_path}" "${new_content}")
            endif()
        endif()
    endforeach()
endfunction()


if(NOT EXISTS "${mecabsrc}/writeonceflag")
  remove_register_from_files(${mecabsrc})
    file(READ "${mecabsrc}/dictionary.cpp" dictionary)
    set(std_binary_function [=[

  template <class Argv1, class Argv2, class Result>
  struct std_binary_function_FUCK
  {
    typedef Argv1 first_argument_type;
    typedef Argv2 second_argument_type;
    typedef Result result_type;
  };
]=])
    string(REPLACE "std::binary_function" "std_binary_function_FUCK" dictionary "${dictionary}")
    file(WRITE "${mecabsrc}/dictionary.cpp" "${std_binary_function}${dictionary}")

    file(READ "${mecabsrc}/mecab.h" mecabh)
    string(REPLACE "__declspec(dllexport)" "" mecabh "${mecabh}")
    string(REPLACE "__declspec(dllimport)" "" mecabh "${mecabh}")
    file(WRITE "${mecabsrc}/mecab.h" "${mecabh}")

    file(WRITE "${mecabsrc}/writeonceflag" "")
endif()

file(GLOB SOURCES "${mecabsrc}/*.cpp")
list(FILTER SOURCES EXCLUDE REGEX ".*/mecab[a-z\\-]*\\.cpp")

add_library(libmecab ${SOURCES})

target_include_directories(libmecab INTERFACE "${mecabsrc}")
if(MSVC AND (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC"))
    target_compile_options(libmecab PRIVATE /EHsc
                                          /std:c++14
                                          /GL         
                                          /GA       
                                          /Ob2        
                                          /W3         
                                          /nologo    
                                          /Zi        
                                          /wd4800    
                                          /wd4305
                                          /wd4267
                                          /wd4244)
else()
  target_compile_options(libmecab PRIVATE -std=c++14 -w)
endif()
target_compile_definitions(
    libmecab PRIVATE
    -D_CRT_SECURE_NO_DEPRECATE
    -DMECAB_USE_THREAD
    -DDLL_EXPORT
    -DHAVE_GETENV
    -DDIC_VERSION=102
    -DVERSION="0.996"
    -DPACKAGE="mecab"
)
if(WIN32)
    target_compile_definitions(
        libmecab PRIVATE
        -DHAVE_WINDOWS_H
        -DUNICODE
        -D_UNICODE
        -DMECAB_DEFAULT_RC="c:\\\\Program Files\\\\mecab\\\\etc\\\\mecabrc"
    )
else()
    target_compile_definitions(
        libmecab PRIVATE
        -DMECAB_DEFAULT_RC="/dev/null"
        # autotools风格的功能检测宏（src下用HAVE_*条件包含系统头/选择实现）
        -DHAVE_STDINT_H
        -DHAVE_SYS_TYPES_H
        -DHAVE_SYS_STAT_H
        -DHAVE_SYS_MMAN_H
        -DHAVE_FCNTL_H
        -DHAVE_STRING_H
        -DHAVE_UNISTD_H
        -DHAVE_DIRENT_H
        -DHAVE_MMAP
        -DHAVE_PTHREAD_H
        -DHAVE_GCC_ATOMIC_OPS
        -DHAVE_UNSIGNED_LONG_LONG_INT
    )
    find_package(Threads REQUIRED)
    target_link_libraries(libmecab PRIVATE Threads::Threads)
    # 静态库链入.so需要PIC
    set_target_properties(libmecab PROPERTIES POSITION_INDEPENDENT_CODE ON)
endif()