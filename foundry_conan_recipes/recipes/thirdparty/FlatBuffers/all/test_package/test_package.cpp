// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include "flatbuffers/util.h"

#include "flatbuffers/flatbuffers.h"

#include <iostream>

int main(int argc, const char* argv[]) {
  // Test 1: if this block throws the whole test shall fail.
  {
    // Example code taken from <a href="https://google.github.io/flatbuffers/flatbuffers_guide_tutorial.html"/>.
    flatbuffers::FlatBufferBuilder builder(1024);
    auto weapon_one_name = builder.CreateString("Sword");
    // Create a `vector` representing the inventory of the Orc. Each number
    // could correspond to an item that can be claimed after he is slain.
    unsigned char treasure[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    auto inventory = builder.CreateVector(treasure, 10);
  }
  // Test 2: if this call throws or returns zero, then the test shall fail.
  return flatbuffers::FileExists(SCHEMA_FILE) ? 0 : 1;
}
