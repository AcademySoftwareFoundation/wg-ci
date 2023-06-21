#define VULKAN_HPP_DISPATCH_LOADER_DYNAMIC 1
#include <vulkan/vulkan.hpp>

#include <iostream>
#include <memory>
#include <system_error>
#include <vector>

std::string toString_Version(const uint32_t version)
{
  std::string string =
            std::to_string(VK_VERSION_MAJOR(version))
    + "." + std::to_string(VK_VERSION_MINOR(version))
    + "." + std::to_string(VK_VERSION_PATCH(version))
  ;

  return string;
}

int main()
{
  std::cout << "Vulkan (Runtime API) test" << std::endl;
  std::cout << "Vulkan SDK Version: " << toString_Version(VK_HEADER_VERSION_COMPLETE) << std::endl;

  try
  {
    std::unique_ptr<vk::DynamicLoader> dynamicLoader;

    try
    {
        dynamicLoader = std::make_unique<vk::DynamicLoader>();
    }
    catch(const std::exception &e)
    {
      std::cout << "Err: std::exception: '" << e.what() << "'" << std::endl;
      // Return no error (0) as not having Vulkan on a system is allowed.
      return 0;
    }


    {
      auto vkEnumerateInstanceVersion = dynamicLoader->getProcAddress<PFN_vkEnumerateInstanceVersion>("vkEnumerateInstanceVersion");

      uint32_t instanceVersion;
      VkResult result = vkEnumerateInstanceVersion( &instanceVersion);
      if(VK_SUCCESS != result)
      {
        std::cout << "Err: Failed to get instance version" << std::endl;
        return 1;
      }
      std::cout << "Vulkan Instance Version: " << toString_Version(instanceVersion) << std::endl;
    }

    {
      auto vkEnumerateInstanceLayerProperties = dynamicLoader->getProcAddress<PFN_vkEnumerateInstanceLayerProperties>("vkEnumerateInstanceLayerProperties");

      uint32_t layerCount = 0;
      vkEnumerateInstanceLayerProperties( &layerCount, nullptr );

      if ( layerCount > 0 ) {
        std::vector<VkLayerProperties> availableLayers( layerCount );
        vkEnumerateInstanceLayerProperties( &layerCount, availableLayers.data() );

        std::cout << "Available Vulkan instance layers:" << std::endl;
        for ( auto layerProperties : availableLayers ) {
          std::cout << "\t" << layerProperties.layerName << " - " << layerProperties.description << std::endl;
        }
      }
    }
  }
  catch(const vk::SystemError &e)
  {
    std::cout << "Err: vk::SystemError: '" << e.what() << "'" << std::endl;
    return 1;
  }
  catch(const std::exception &e)
  {
    std::cout << "Err: std::exception: '" << e.what() << "'" << std::endl;
    return 1;
  }
  catch (...)
  {
    std::cout << "Err: Unhandled exception" << std::endl;
    return 1;
  }

  return 0;
}
