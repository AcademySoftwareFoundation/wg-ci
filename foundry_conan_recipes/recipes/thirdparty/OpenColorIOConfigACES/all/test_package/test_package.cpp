// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

// This test package tests the ACES 1.3 OCIO configs that make up the package
// If the config is not valid, the call to validate() will throw, which will cause test to fail

#include <OpenColorIO/OpenColorIO.h>
namespace OCIO = OCIO_NAMESPACE;

#include <filesystem>

void validateConfig(const char* configPath)
{
  OCIO::ConstConfigRcPtr config = OCIO::Config::CreateFromFile(configPath);
  config->validate();
}

int main()
{
  const std::string configExtension = ".ocio";
  for (const auto& dir_entry : std::filesystem::directory_iterator{std::filesystem::current_path()}) {
    if (dir_entry.path().extension() == configExtension) {
      const std::string currentPath = dir_entry.path();
      validateConfig(currentPath.c_str());
    }
  }
}
