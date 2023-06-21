# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile


class TestPackageConan(ConanFile):
    settings = 'os', 'compiler', 'build_type', 'arch'

    def test(self):
        self.run(['flex', '--version'])
        self.run(['flex', os.path.join(os.path.dirname(__file__), 'testxxLexer.l')])
