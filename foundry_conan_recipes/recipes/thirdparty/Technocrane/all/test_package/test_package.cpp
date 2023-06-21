// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <iostream>
#include "technocrane_hardware.h"

int main() {
    NTechnocrane::CTechnocrane_Hardware hardware{};
    NTechnocrane::SOptions options = hardware.GetOptions();
    std::cout << "Network port: " << options.m_NetworkPort << std::endl;

    return 0;
}
