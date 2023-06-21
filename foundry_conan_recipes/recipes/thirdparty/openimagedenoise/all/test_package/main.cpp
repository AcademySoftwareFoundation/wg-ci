//
// Copyright (c) 2022 The Foundry Visionmongers Ltd.  All Rights Reserved.
//

#include <OpenImageDenoise/oidn.hpp>

int main()
{
    oidn::DeviceRef device = oidn::newDevice();

    bool const errorIsNone = static_cast<int>(device.getError()) == OIDN_ERROR_NONE;

    return errorIsNone ? 0 : -1;
}
