// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <iostream>
#include <lcms2.h>

int main(void) {

    std::cout << "[TEST] LITTLECMS VERSION: " << LCMS_VERSION << std::endl;
    std::cout << "[TEST] LITTLECMS ENCODED VERSION: " << cmsGetEncodedCMMversion() << std::endl;

    return 0;
}
