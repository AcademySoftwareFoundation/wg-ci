# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def config_options(self):
        if "python_version" in self.options["MaterialX"] and self.options["MaterialX"].python_version:
            self.options["OpenColorIO"].python_version = self.options["MaterialX"].python_version

    def imports(self):
        if "python_version" in self.options["MaterialX"] and self.options["MaterialX"].python_version:
            python_version = self.options['MaterialX'].python_version
            self.copy("*.pyd", "", "lib/site-packages",
                      root_package="OpenColorIO")
            self.copy("*.dll", "", "bin", root_package="OpenColorIO")
            self.copy("*.so*", "", "lib64", root_package="OpenColorIO")
            self.copy("*.so*", "", f"lib64/python{python_version}/site-packages",
                      root_package="OpenColorIO")
            self.copy("*.so*", "", f"lib/python{python_version}/site-packages",
                      root_package="OpenColorIO")
            self.copy("*.dylib", "", "lib", root_package="OpenColorIO")

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(
            self.install_folder, "conan_paths.cmake")
        if self.options["MaterialX"].python_version:
            cmake.definitions["Python_ROOT_DIR"] = self.deps_cpp_info["Python"].rootpath
            cmake.definitions["RUN_PYTHON_BINDINGS_TESTS"] = "ON"
        if self.settings.os == 'Macos':
            cmake.definitions["CMAKE_FIND_FRAMEWORK"] = 'LAST'
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
