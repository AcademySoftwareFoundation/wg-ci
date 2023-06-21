// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <iostream>
#include <minizip/unzip.h>
#include <minizip/zip.h>

int main(void) {
    unzFile zipFile = unzOpen("./testFile.zip");
    if (!zipFile) {
        return 1;
    }
    if (unzCloseCurrentFile(zipFile) == UNZ_CRCERROR)
    {
        return 1;
    }

    unzFile badZipFile = unzOpen("./ThisFileDoesNotExist.zip");
    if (badZipFile) 
    {
        return 1;
    }

    std::cout << ZIP_OK << std::endl;
    return 0;
}