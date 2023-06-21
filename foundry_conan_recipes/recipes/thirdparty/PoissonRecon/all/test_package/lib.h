#ifndef LIB_H
#define LIB_H

#ifdef _MSC_VER
#   ifdef lib_EXPORTS
#       define LIB_API __declspec(dllexport)
#   else
#       define LIB_API __declspec(dllimport)
#   endif
#else
#   define LIB_API __attribute__((visibility("default")))
#endif

extern LIB_API void PoissonTest();

#endif // LIB_H
