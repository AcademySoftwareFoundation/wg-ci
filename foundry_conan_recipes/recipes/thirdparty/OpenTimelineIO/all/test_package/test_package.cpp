// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <opentimelineio/timeline.h>
#include <opentime/rationalTime.h>
#include <iostream>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

int main()
{
   otio::SerializableObject::Retainer<otio::Timeline> timeline;
   otio::RationalTime rt;
   std::cout << rt.to_time_string() << std::endl;

   return 0;
}
