#include <iostream>
#include "sqlite3.h"

int main() {
    std::cout << "SQLite version " << sqlite3_libversion() << std::endl;
    return 0;
}
