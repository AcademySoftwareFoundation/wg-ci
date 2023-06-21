// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <iostream>
#include <MaterialXCore/Util.h>

int main(void)
{
    std::cout << "[TEST] MaterialX VERSION: " << MaterialX::getVersionString() << std::endl;
    return 0;
}
