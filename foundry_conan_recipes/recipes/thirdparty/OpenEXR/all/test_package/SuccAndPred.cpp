#include <iostream>
#include <limits>

#include "OpenEXR/ImathFun.h"

int main()
{
    // Test to cover a regression in `Imath::succf()` and `Imath::predf()`.
    // See:
    // - https://github.com/AcademySoftwareFoundation/openexr/issues/999
    // - https://github.com/AcademySoftwareFoundation/openexr/pull/998

    const float values[] = {std::numeric_limits<float>::min(),
                            -1.5f,
                            -1.0f,
                            -0.5f,
                            0.0f * -1.0f,
                            0.0f,
                            0.5f,
                            1.0f,
                            1.5f,
                            2.0f,
                            std::numeric_limits<float>::max()};

    for (const float v : values)
    {
        if (Imath::succf(v) <= v)
        {
            std::cout << "Successor of " << v << " should be greater than " << v
                      << std::endl;
            return 1;
        }
        if (Imath::predf(v) >= v)
        {
            std::cout << "Predecessor of " << v << " should be less than " << v
                      << std::endl;
            return 1;
        }
    }

    return 0;
}
