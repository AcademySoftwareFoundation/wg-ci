# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import subprocess

from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = 'os', 'compiler', 'build_type', 'arch'

    def build(self):
        pass

    def test(self):
        actions_and_expected_output = (
            ('--validate', ''),
            ('--modversion', '1.0.0'),
            ('--libs', '-lfoo'),
            ('--cflags', '-I/usr/include/foo'),
        )

        pkgconfig_path = os.path.join(
            self.deps_cpp_info['pkgconfig'].bin_paths[0], 'pkg-config')

        for action, expected_output in actions_and_expected_output:
            with tools.chdir(self.source_folder):
                # don't use self.run as CONAN_PRINT_RUN_COMMANDS can add extra output
                output = subprocess.check_output([pkgconfig_path, action, "foo.pc"]).decode("utf-8").strip()

            if output != expected_output:
                raise RuntimeError('"{}" != "{}"'.format(
                    output, expected_output))
