#include "OpenEXR/ImfRgbaFile.h"

// Checking this include because it is routinely forgotten to be installed
#include "OpenEXR/ImfMisc.h"

#include <iostream>

int main(int argc, const char* argv[]) {
  if (argc != 2) {
    return 1;
  }

  Imf::RgbaInputFile input(argv[1]);
  const auto& header = input.header();
  const auto width = header.dataWindow().max.x - header.dataWindow().min.x + 1;
  const auto height = header.dataWindow().max.y - header.dataWindow().min.y + 1;
  std::cout << "Image dimensions are: " << width << "x" << height << std::endl;
  return 0;
}
