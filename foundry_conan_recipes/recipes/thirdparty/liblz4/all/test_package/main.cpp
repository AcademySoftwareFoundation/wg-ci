#include <lz4.h>
#include <iostream>

int main() {
    std::cout << "LZ4 Library version = " << LZ4_versionNumber() << std::endl;
    return 0;
}
