// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include "json.h"

int main() {
  const QVariant data(true);
  const QByteArray serialised=QtJson::serialize(data);
  if (serialised=="true") {
    return 0;
  } else {
    return 1;
  }
}
