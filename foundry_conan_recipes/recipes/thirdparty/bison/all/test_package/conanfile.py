# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile


class TestPackageConan(ConanFile):
    settings = 'os', 'compiler', 'build_type', 'arch'

    def test(self):
        self.run(['bison', '--version'])
        self.run(['bison', '-d', os.path.join(os.path.dirname(__file__), 'mc_parser.yy')])
