#include <cudnn.h>
#include <iostream>

int main() {
  auto version_number = cudnnGetVersion();
  std::cout << "cuDNN version " << version_number << std::endl;
  return 0;
}