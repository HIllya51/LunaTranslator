cmake_minimum_required(VERSION 3.28)

set(CMAKE_C_STANDARD 11)

include(FetchContent)
FetchContent_Declare(
        curl
        URL "https://github.com/curl/curl/archive/refs/tags/curl-8_11_1.tar.gz"
        OVERRIDE_FIND_PACKAGE
)
FetchContent_Declare(
        openssl
        URL "https://github.com/janbar/openssl-cmake/archive/refs/tags/1.1.1w-20231130.tar.gz"
        OVERRIDE_FIND_PACKAGE
)
FetchContent_MakeAvailable(openssl)

add_library(OpenSSL::SSL INTERFACE IMPORTED)
target_link_libraries(OpenSSL::SSL INTERFACE ssl)
add_library(OpenSSL::Crypto INTERFACE IMPORTED)
target_link_libraries(OpenSSL::Crypto INTERFACE crypto)
set(BUILD_STATIC_LIBS OFF CACHE INTERNAL "Build static libraries" FORCE)
set(BUILD_SHARED_LIBS ON CACHE INTERNAL "Switch off building shared libraries" FORCE)
set(ENABLE_WEBSOCKETS ON CACHE INTERNAL "Set to ON to enable EXPERIMENTAL websockets" FORCE)
set(BUILD_CURL_EXE OFF CACHE BOOL "Switch off building curl executable" FORCE)
set(BUILD_TESTING OFF CACHE INTERNAL "Switch off building curl tests" FORCE)
set(CURL_USE_OPENSSL ON CACHE INTERNAL "Use OpenSSL backend" FORCE)

FetchContent_MakeAvailable(curl)
