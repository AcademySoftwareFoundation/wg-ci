// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <iostream>

#include "unzip.h"
#include "zip.h"

int main(void) {
    unzFile zipFile = unzOpen("./testFile.zip");
    if (!zipFile)
    {
        std::cerr << "ERROR: Unable to open ZIP file." << std::endl;
        return 1;
    }
    if (unzCloseCurrentFile(zipFile) == UNZ_CRCERROR)
    {
        std::cerr << "ERROR: Unable to close ZIP file." << std::endl;
        return 1;
    }

    unzFile badZipFile = unzOpen("./ThisFileDoesNotExist.zip");
    if (badZipFile)
    {
        std::cerr << "ERROR: Unexpected success while open missing ZIP file." << std::endl;
        return 1;
    }

    std::cout << ZIP_OK << std::endl;
    return 0;
}
