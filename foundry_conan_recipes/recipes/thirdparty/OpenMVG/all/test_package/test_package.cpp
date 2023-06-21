// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include "openMVG/cameras/Camera_Common.hpp"
#include "openMVG/cameras/cameras.hpp"
#include "openMVG/cameras/PinholeCamera.hpp"

#include "openMVG/sfm/sfm_data.hpp"
#include "openMVG/sfm/sfm_data_utils.hpp"

#include "openMVG/sfm/pipelines/sfm_features_provider.hpp"
#include "openMVG/sfm/pipelines/sfm_matches_provider.hpp"
#include "openMVG/sfm/pipelines/global/sfm_global_engine_relative_motions.hpp"
#include "openMVG/sfm/pipelines/sequential/sequential_SfM.hpp"

int main() {
    openMVG::Mat3 rotation = openMVG::Mat3::Identity();
    openMVG::Vec3 centre = openMVG::Vec3::Zero();
    openMVG::sfm::SfM_Data data;
    return 0;
}

