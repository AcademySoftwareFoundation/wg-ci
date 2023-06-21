// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <llvm/Support/raw_ostream.h>
#include <iostream>

int main() {
  std::string str;
  llvm::raw_string_ostream sstream(str);
  sstream << "test";
  if (sstream.str() == "test") {
    std::cout << "[SUCCESS] Package built successfully." << std::endl;
    return 0;
  }
  std::cout << "[FAILURE] Package failed to build." << std::endl;
  return -1;
}
