#include <iostream>
#include <cupti_version.h>

int main()
{
  uint32_t version = 0;
  auto result = cuptiGetVersion(&version);
  if (result != CUPTI_SUCCESS) {
    return 1;
  }
  std::cout << "CUPTI version " << version << " found!" << std::endl;
  return 0;
}
