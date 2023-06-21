#include "bzlib.h"

#include <iostream>

int main() {
    std::cout << "bzip2 version: " << BZ2_bzlibVersion() << std::endl;
    return 0;
}
