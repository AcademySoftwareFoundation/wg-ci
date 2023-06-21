# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    name = "openassetio-test"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"
    # Only mode available in Conan 2 is "explicit":
    #   https://docs.conan.io/en/latest/migrating_to_2.0/recipes.html#changes-in-the-test-package-recipe
    test_type = "explicit"

    def requirements(self):
        # Since test_type "explicit" / Conan 2 compatibility.
        self.requires(self.tested_reference_str)
        # Bring in Python for tests, if required.
        # Note: substitution of unspecified options with their default
        # value hasn't happened by this point, but we can test if the
        # option has been provided, at least.
        if "python_version" in self.options["openassetio"]:
            self.requires(f"Python/[~{self.options['openassetio'].python_version}]")

    def test(self):
        version_data = self.conan_data["sources"][self.deps_cpp_info["openassetio"].version]
        checkout_folder = os.path.join(self.build_folder, f"{self.name}_src")

        git = tools.Git(folder=checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

        cmake = CMake(self)

        # Teach CMake's `find_package` where to look.
        cmake.definitions["CMAKE_PROJECT_OpenAssetIO-Test-CMake_INCLUDE"] = os.path.join(
            self.install_folder, "conan_paths.cmake"
        )

        # C++ ABI for GCC. VFX <= CY2022 uses old ABI.
        libcxx = self.settings.get_safe("compiler.libcxx")
        if libcxx is not None:
            if libcxx == "libstdc++11":
                cmake.definitions["OPENASSETIOTEST_GLIBCXX_USE_CXX11_ABI"] = "ON"
            else:
                cmake.definitions["OPENASSETIOTEST_GLIBCXX_USE_CXX11_ABI"] = "OFF"

        if not self.options["openassetio"].python_version:
            cmake.definitions["OPENASSETIOTEST_ENABLE_PYTHON"] = "OFF"
        else:
            cmake.definitions["OPENASSETIOTEST_ENABLE_PYTHON"] = "ON"
            # Ensure identical Python is used.
            cmake.definitions["Python_EXECUTABLE"] = self._python_exe
            if self.settings.os == "Windows":
                cmake.definitions["Python_LIBRARY"] = self._python_lib

        cmake.definitions["OPENASSETIOTEST_ENABLE_C"] = "OFF"
        cmake.configure(source_folder=checkout_folder)
        cmake.build()
        cmake.test(output_on_failure=True)

    @property
    def _python_exe(self):
        # Note: ConanCenter recipe differs in providing
        # `user_info.python`, giving an absolute path to the
        # executable.
        return os.path.join(
            self.deps_cpp_info["Python"].rootpath,
            self.deps_user_info["Python"].interpreter)

    @property
    def _python_lib(self):
        return os.path.join(
            self.deps_cpp_info["Python"].rootpath,
            self.deps_cpp_info["Python"].libdirs[0], self.deps_cpp_info["Python"].libs[0])
