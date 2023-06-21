// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <iostream>
#include <openjpeg.h>

int main()
{
    std::cout << "opj_version: " << opj_version() << std::endl;
}

