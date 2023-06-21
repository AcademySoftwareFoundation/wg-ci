#include <cstring>

#include "sqlcipher/sqlite3.h"

int main()
{
    const char* const version = sqlite3_libversion();
    return (version && strlen(version) > 0) ? 0 : 1;
}
