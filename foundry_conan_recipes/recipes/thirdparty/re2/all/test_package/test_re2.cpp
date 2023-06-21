#include "re2/re2.h"

int main()
{
    // snippets borrowed from the re2.h header file comment
    if (!RE2::FullMatch("hello", "h.*o"))
    {
        return 1;
    }
    if (RE2::FullMatch("hello", "e"))
    {
        return 2;
    }
    return 0;
}
