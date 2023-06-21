// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <stdlib.h>

#include <GLFW/glfw3.h>


int main()
{
    int version[3] = { -1, -1, -1 };
    glfwGetVersion(&version[0], &version[1], &version[2]);
    if ((version[0] == -1) || (version[1] == -1) || (version[2] == -1)) {
        return EXIT_FAILURE;
    }

    const char *versionStr = glfwGetVersionString();
    if (!versionStr) {
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
