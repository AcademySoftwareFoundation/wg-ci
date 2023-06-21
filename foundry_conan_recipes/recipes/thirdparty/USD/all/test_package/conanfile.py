# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os, semver

from conans import ConanFile, CMake
from conans.errors import ConanException


class UsdTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    @property
    def _testOpenVDB(self) -> bool:
        return "OpenVDB" in self.deps_cpp_info.deps

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["shared_usd"] = self.options["USD"].shared
        cmake.definitions["with_imaging"] = self.options["USD"].imaging
        cmake.definitions["test_openvdb"] = self._testOpenVDB
        if self.options["USD"].python_bindings:
            cmake.definitions["with_python_bindings"] = "TRUE"
            cmake.definitions["CONAN_PYHOME"] = os.path.join(self.deps_cpp_info["Python"].rootpath, self.deps_user_info["Python"].pyhome).replace("\\", "/")
            cmake.definitions["CONAN_PYTHON_INTERPRETER"] = os.path.join(self.deps_cpp_info["Python"].rootpath, self.deps_user_info["Python"].interpreter).replace("\\", "/")

            # py_version = tools.Version(self.deps_cpp_info["Python"].version)
            # cmake.definitions["CONAN_PYTHON_VERSION"] = f"{py_version.major}.{py_version.minor}"

        # Setup the PXR_PY_PACKAGE_NAME so we can use it to replace the pxr
        # package name in our test at build time.
        if self.options["USD"].namespace:
            cmake.definitions["PXR_PY_PACKAGE_NAME"] = self.deps_user_info["USD"].PXR_PY_PACKAGE_NAME
        else:
            cmake.definitions["PXR_PY_PACKAGE_NAME"] = "pxr"

        cmake.configure()
        cmake.build()
        cmake.parallel = False # since bootstrap.py can perform the same option (e.g. pip install) on multiple runs
        cmake.test(output_on_failure=True)
