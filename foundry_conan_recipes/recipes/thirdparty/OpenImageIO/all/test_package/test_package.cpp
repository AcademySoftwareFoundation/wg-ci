// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <iostream>
#include <OpenImageIO/imageio.h>

int main(void)
{
    std::cout << "[TEST] OPENIMAGE_IO VERSION: " << OIIO::openimageio_version() << std::endl;
    return 0;
}

