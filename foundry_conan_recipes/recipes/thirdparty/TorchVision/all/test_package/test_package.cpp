// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <iostream>
#include <torchvision/vision.h>

int main ()
{
  std::cout << "[TEST] TorchVision cuda_version = " << vision::cuda_version() << std::endl;
  return 0;
}
