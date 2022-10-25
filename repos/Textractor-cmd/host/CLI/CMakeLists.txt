# The CLI isn't used by Textractor itself, but is here for other people that want to build projects on top of Textractor
add_executable(TextractorCLI "main.cpp")
target_precompile_headers(TextractorCLI REUSE_FROM pch)
target_link_libraries(TextractorCLI host)
