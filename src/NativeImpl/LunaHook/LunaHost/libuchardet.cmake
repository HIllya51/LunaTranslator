
include(FetchContent)

FetchContent_Declare(uchardet
    GIT_REPOSITORY https://gitlab.freedesktop.org/uchardet/uchardet.git
    GIT_TAG 06029ec3340cdf6bf9a6a537dafb3f39eda0560e
    GIT_SHALLOW TRUE
)
FetchContent_Populate(uchardet)

set(uchardetsrc "${uchardet_SOURCE_DIR}/src")

if(NOT EXISTS "${uchardetsrc}/lunatranslator_patched")
    file(READ "${uchardetsrc}/nsMBCSGroupProber.cpp" groupprober)
    string(REGEX REPLACE "[ \t]*langDetectors\\[i\\]\\[j\\+\\+\\] *= *new nsLanguageDetector\\([^)]*\\);[ \t]*[\r\n]+" "" groupprober "${groupprober}")
    string(REPLACE "mProbers[0] = new nsUTF8Prober();" "" groupprober "${groupprober}")
    string(REPLACE "if (mProbers[i]->DecodeToUnicode())" "if (0)" groupprober "${groupprober}")
    string(REPLACE "codePointBufferSize[i] == 0 && mProbers[i]->DecodeToUnicode()" "codePointBufferSize[i] == 0 && 0" groupprober "${groupprober}")

    string(FIND "${groupprober}" "new nsLanguageDetector(&" pos)
    if(NOT pos EQUAL -1)
        message(FATAL_ERROR "uchardet patch failed: model refs remain")
    endif()
    string(FIND "${groupprober}" "new nsUTF8Prober" pos)
    if(NOT pos EQUAL -1)
        message(FATAL_ERROR "uchardet patch failed: utf8 prober still enabled")
    endif()
    string(REGEX MATCHALL "if \\(0\\)" hits "${groupprober}")
    list(LENGTH hits nhits)
    if(NOT nhits EQUAL 2)
        message(FATAL_ERROR "uchardet patch failed: expected 2 flipped conditions, got ${nhits}")
    endif()
    if(NOT groupprober MATCHES "codePointBufferSize\\[i\\] == 0 && 0")
        message(FATAL_ERROR "uchardet patch failed: codepoint buffer alloc not disabled")
    endif()
    file(WRITE "${uchardetsrc}/nsMBCSGroupProber.cpp" "${groupprober}")

    file(READ "${uchardetsrc}/nsUniversalDetector.cpp" universal)
    string(REPLACE
        "        if (nsnull == mCharSetProbers[1] &&
            (mLanguageFilter & NS_FILTER_NON_CJK))
        {
          mCharSetProbers[1] = new nsSBCSGroupProber;
          if (nsnull == mCharSetProbers[1])
            return NS_ERROR_OUT_OF_MEMORY;
        }"
        "        /* LunaTranslator trim: SBCS group is not built. */"
        universal "${universal}")
    string(FIND "${universal}" "new nsSBCSGroupProber" pos)
    if(NOT pos EQUAL -1)
        message(FATAL_ERROR "uchardet patch failed: SBCS group still created")
    endif()
    file(WRITE "${uchardetsrc}/nsUniversalDetector.cpp" "${universal}")

    file(WRITE "${uchardetsrc}/lunatranslator_patched" "")
endif()

file(GLOB SOURCES "${uchardetsrc}/*.cpp")
list(FILTER SOURCES EXCLUDE REGEX "nsSBCSGroupProber|nsSBCharSetProber|nsHebrewProber")
add_library(libuchardet STATIC ${SOURCES})
target_include_directories(libuchardet INTERFACE "${uchardetsrc}")
