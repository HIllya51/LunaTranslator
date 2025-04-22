
include(FetchContent)

FetchContent_Declare(mecab
    GIT_REPOSITORY https://github.com/ikegami-yukino/mecab
    GIT_TAG db005dc77e92290b8834121a18eaca0c6227f438
)
FetchContent_Populate(mecab)

set(mecabsrc "${mecab_SOURCE_DIR}/mecab/src")

if(NOT EXISTS "${mecabsrc}/writeonceflag")

    if(NOT WINXP)
        file(READ "${mecabsrc}/dictionary.cpp" dictionary)
        set(std_binary_function [=[
namespace std
{
  template <class Argv1, class Argv2, class Result>
  struct binary_function
  {
    typedef Argv1 first_argument_type;
    typedef Argv2 second_argument_type;
    typedef Result result_type;
  };
}
]=])
        file(WRITE "${mecabsrc}/dictionary.cpp" "${std_binary_function}${dictionary}")
    else()

    endif()

    file(READ "${mecabsrc}/mecab.h" mecabh)
    string(REPLACE "__declspec(dllexport)" "" mecabh "${mecabh}")
    string(REPLACE "__declspec(dllimport)" "" mecabh "${mecabh}")
    file(WRITE "${mecabsrc}/mecab.h" "${mecabh}")

    file(WRITE "${mecabsrc}/writeonceflag" "")
endif()

file(GLOB SOURCES "${mecabsrc}/*.cpp")
list(FILTER SOURCES EXCLUDE REGEX ".*/mecab-[a-z\\-]*\\.cpp")

add_library(libmecab ${SOURCES})

target_include_directories(libmecab INTERFACE "${mecabsrc}")
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
target_compile_definitions(
    libmecab PRIVATE
    -D_CRT_SECURE_NO_DEPRECATE
    -DMECAB_USE_THREAD
    -DDLL_EXPORT
    -DHAVE_GETENV
    -DHAVE_WINDOWS_H
    -DDIC_VERSION=102
    -DVERSION="0.996"
    -DPACKAGE="mecab"
    -DUNICODE
    -D_UNICODE
    -DMECAB_DEFAULT_RC="c:\\\\Program Files\\\\mecab\\\\etc\\\\mecabrc"
)