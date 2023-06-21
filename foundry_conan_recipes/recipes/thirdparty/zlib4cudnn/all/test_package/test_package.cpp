// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#ifdef _WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif

#include <cstdlib>
#include <iostream>

#define STRINGIFY_(x) #x
#define STRINGIFY(x) STRINGIFY_(x)

void load_error(const char* path)
{
    std::cerr << "Failed to load library: " << path << std::endl;
#if defined(__APPLE__) || defined(__linux__)
    std::cerr << dlerror() << std::endl;
#endif
    std::exit(1);
}

void symbol_error(const char* sym)
{
    std::cerr << "Failed to find symbol: " << sym << std::endl;
#if defined(__APPLE__) || defined(__linux__)
    std::cerr << dlerror() << std::endl;
#endif
    std::exit(1);
}

template<typename HandleType>
void close_library(HandleType handle)
{
#ifdef _WIN32
    FreeLibrary(handle);
#else
    dlclose(handle);
#endif
}

template<typename HandleType>
void check_loaded(HandleType handle, const char* path)
{
    if(!handle)
    {
        load_error(path);
    }
}

int main(void) {
    using funcp_t = const char*(*)(void);
    funcp_t zlibVersion = nullptr;
    const char* library_to_load = STRINGIFY(LIBRARY_TO_LOAD);
    const char* symbol_to_load = "zlibVersion";

#if _WIN32
    HINSTANCE lib = LoadLibrary(library_to_load);
    check_loaded(lib, library_to_load);
    zlibVersion = reinterpret_cast<funcp_t>(GetProcAddress(lib, symbol_to_load));
#else
    void* lib = dlopen(library_to_load, RTLD_LAZY);
    check_loaded(lib, library_to_load);
    zlibVersion = reinterpret_cast<funcp_t>(dlsym(lib, symbol_to_load));
#endif

    if(!zlibVersion)
    {
        symbol_error(symbol_to_load);
    }

    std::cout << "[TEST] ZLIB VERSION: " << zlibVersion() << std::endl;

    close_library(lib);

    return 0;
}
