# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile


class TestPackage(ConanFile):
    settings = 'os', 'compiler', 'build_type', 'arch'

    def test(self):
        executable = os.path.join(self.deps_cpp_info['yasm'].bin_paths[0], 'yasm')

        self.run([executable, '--license'])
