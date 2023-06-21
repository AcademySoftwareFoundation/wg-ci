// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include "tiffio.h"
int main()
{
    TIFF* tif = TIFFOpen("foo.tif", "w");
    TIFFClose(tif);
}

