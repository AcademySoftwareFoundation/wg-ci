# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import subprocess

from conans import ConanFile


class TestPackageConan(ConanFile):
    settings = 'os', 'compiler', 'build_type', 'arch'

    def test(self):
        binary = os.path.join(self.deps_cpp_info['win-flex-bison'].bin_paths[0], 'win_bison')

        subprocess.check_call([binary, '--version'])
        subprocess.check_call([binary, '-d', os.path.join(os.path.dirname(__file__), 'mc_parser.yy')])
