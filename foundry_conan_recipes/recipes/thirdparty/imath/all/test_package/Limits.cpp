#include <limits>
#include <iostream>
#include "Imath/ImathColor.h"

int main()
{
    auto halfMax = std::numeric_limits<Imath::half>::max();
    auto halfMin = std::numeric_limits<Imath::half>::min();
    auto c4hMax = Imath::Color4h::baseTypeMax();
    auto c4hMin = Imath::Color4h::baseTypeSmallest();

    std::cout << "halfMax: " << halfMax << std::endl;
    std::cout << "c4hMax: " << halfMax << std::endl;
    std::cout << "HALF_MAX: " << HALF_MAX << std::endl;
    std::cout << "halfMin: " << halfMin << std::endl;
    std::cout << "c4hMin: " << c4hMin << std::endl;
    std::cout << "HALF_MIN: " << HALF_MIN << std::endl;

    return halfMax == HALF_MAX && c4hMax == HALF_MAX && halfMin == HALF_MIN && c4hMin == HALF_MIN ? 0 : 1;
}
