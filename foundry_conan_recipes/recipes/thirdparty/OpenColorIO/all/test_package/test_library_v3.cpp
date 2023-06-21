#include <regex>
#include <string>
#include <iostream>
#include <cassert>

#include <OpenColorIO/OpenColorIO.h>
#include <OpenColorIO/OpenColorAppHelpers.h>
namespace OCIO = OCIO_NAMESPACE;

int main()
{
  const std::string actualVersion(OCIO::GetVersion());
  std::cout << "OCIO Version: " << actualVersion << std::endl;
  std::regex pat(std::string(OCIO_CONFIGURED_VERSION) + std::string("($|dev|beta.?|rc?)"));
  assert(std::regex_search(actualVersion, pat));  // suffix appears for debug build

  const std::string configPath("aces_1.0.3/config.ocio");
  OCIO::ConstConfigRcPtr config = OCIO::Config::CreateFromFile(configPath.c_str());
  config->validate(); // throws exception if anything is wrong
  std::cout << "OCIO Loaded Config: " << configPath << std::endl;

  const std::string colorSpace("ACES - ACES2065-1");
  assert(config->getColorSpace(colorSpace.c_str()));
  std::cout << "OCIO Config Has ColorSpace: " << colorSpace << std::endl;

  OCIO::LegacyViewingPipelineRcPtr pipeline = OCIO::LegacyViewingPipeline::Create();
  pipeline->setLooksOverride("something");
  assert(strcmp(pipeline->getLooksOverride(), "something") == 0);

  return 0;
}
