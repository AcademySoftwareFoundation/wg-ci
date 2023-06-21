// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <iostream>
#include <zlib.h>

int main(void) {

    std::cout << "[TEST] ZLIB VERSION: " << zlibVersion() << std::endl;

    return 0;
}