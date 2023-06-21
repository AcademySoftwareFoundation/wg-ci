// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

extern "C" {
#include "SHA3api_ref.h"
}

#include <array>

int main() {
  const std::array<BitSequence, 32> Msg={};
  std::array<BitSequence, 32> MD={};
  const int ret=Hash(224, Msg.data(), 0, MD.data());
  const std::array<BitSequence, 32> MD_result={0x50, 0x46, 0x2A, 0x68, 0x05, 0xB7, 0x40, 0x17, 0xAC, 0x85, 0x23, 0x70, 0x77, 0xFB, 0x12, 0x2A, 0x50, 0x79, 0x11, 0xB7, 0x37, 0xC9, 0xA6, 0x6F, 0xF0, 0x56, 0xA8, 0x23};
  if (MD!=MD_result) {
    return -1;
  } else {
    return ret;
  }
}
