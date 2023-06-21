# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile


class TestPackageConan(ConanFile):
    settings = 'os', 'arch'

    def test(self):
        ispc_path = os.path.normpath(os.path.join(self.deps_cpp_info['ispc'].bin_paths[0], 'ispc'))

        self.run([ispc_path, os.path.join(self.source_folder, 'test.ispc')])
