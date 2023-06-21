# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil
import tempfile

from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires('LuaJIT/2.1.0-beta3.2@thirdparty/development')

    def config_options(self):
        self.options['LuaJIT'].shared = False

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build(self):
        pass

    def test(self):
        # To ensure SWIG is relocatable, it will be executed from a temporary directory.
        with tempfile.TemporaryDirectory() as tmp_dir:
            luajit_dir = self.deps_cpp_info['LuaJIT'].rootpath
            swig_dir = self.deps_cpp_info['SWIG'].rootpath

            # Copy SWIG to a temporary location.
            swig_tmp_dir = os.path.join(tmp_dir, 'swig')
            shutil.copytree(swig_dir, swig_tmp_dir)

            # The original location of the package is temporarily renamed, ensuring that potentially
            # hardcoded paths in the executable are invalidated.
            os.rename(swig_dir, f'{swig_dir}_hidden')
            try:
                with tools.environment_append({'CMAKE_PREFIX_PATH': [swig_tmp_dir, luajit_dir]}):
                    cmake = CMake(self)
                    cmake.configure()
                    cmake.build()
                    cmake.test(output_on_failure=True)
            finally:
                # Restore original name.
                os.rename(f'{swig_dir}_hidden', swig_dir)
