// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <cstdio>
#include "portaudio.h"

int main(void)
{
    printf("PortAudio version: 0x%08X\n", Pa_GetVersion());
    return 0;
}
