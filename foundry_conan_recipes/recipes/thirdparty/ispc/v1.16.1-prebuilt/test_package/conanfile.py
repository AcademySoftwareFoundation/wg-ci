# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from io import StringIO
import os
import re

from conans import ConanFile

# Run the ispc executable and ensure that the version number it outputs matches the version
# number of the recipe.
class TestPackageConan(ConanFile):
    settings = 'os', 'compiler', 'build_type', 'arch'

    def build(self):
        pass

    def test(self):
        ispc_path = os.path.normpath(os.path.join(
            self.deps_cpp_info['ispc'].bin_paths[0], 'ispc'))

        buffer = StringIO()
        self.run(f'"{ispc_path}" --version', output=buffer)
        output = buffer.getvalue().strip()

        matches = re.findall('(\d+\.\d+\.\d)', output)
        search = self.deps_cpp_info['ispc'].version.replace('-prebuilt', '')

        if matches and len(matches) >= 1 and search in matches:
            self.output.info(f'"{matches[0]}" == "{search}"')
        else:
            raise RuntimeError(f'"{matches[0]}" != "{search}"')
