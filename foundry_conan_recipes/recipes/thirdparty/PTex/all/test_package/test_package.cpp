// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include "Ptexture.h"
using namespace Ptex;

int main(int argc, char** argv)
{
    PtexPtr<PtexCache> testCache(PtexCache::create(0, 1024*1024));
    return 0;
}

