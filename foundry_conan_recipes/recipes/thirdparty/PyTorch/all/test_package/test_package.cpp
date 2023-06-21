// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <ATen/Version.h>
#include <iostream>


int main () {
    std::string config = at::show_config();

    if (0 == config.size()) {
        std::cout << "[FAILURE]" << std::endl;
    	return 1;
    }
    std::cout << "[SUCCESS] PyTorch Config:" << config << std::endl;
    return 0;
}
