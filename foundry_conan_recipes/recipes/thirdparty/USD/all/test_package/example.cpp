#include "pxr/pxr.h"
#include "pxr/base/arch/threads.h"

#include <iostream>

int main() {
    std::cout << "USD version: " << PXR_VERSION << std::endl;
    std::cout << "ArchIsMainThread(): " << PXR_NS::ArchIsMainThread() << std::endl;
    return 0;
}

