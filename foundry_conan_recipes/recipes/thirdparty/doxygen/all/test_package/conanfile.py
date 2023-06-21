# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import subprocess

from conans import ConanFile


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def build(self):
        pass

    def test(self):
        doxygen_bin_dir = self.deps_cpp_info['Doxygen'].bin_paths[0]
        if not os.path.isdir(doxygen_bin_dir):
            raise RuntimeError(f'Doxygen `bin` dir not valid: "{doxygen_bin_dir}"')

        doxygen_path = os.path.join(doxygen_bin_dir, self.deps_user_info['Doxygen'].executable)
        if not os.path.isfile(doxygen_path):
            raise RuntimeError(f'Doxygen executable path not valid: "{doxygen_path}"')

        output = subprocess.check_output((doxygen_path, '--version'), text=True)
        version = self.deps_cpp_info['Doxygen'].version
        if not output.startswith(version):
            raise RuntimeError(f'Version ({version}) not found in command output:\n{output}')
