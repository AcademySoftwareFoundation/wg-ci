# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def imports(self):
        self.copy("*.dylib", dst=".", src=os.path.join("python", "opentimelineio")) # due to the use of @loader_path for install names for OTIO >= 0.14

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_OpenTimelineIOTest_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["shared"] = self.options["OpenTimelineIO"].shared
        cmake.definitions["CONAN_PYHOME"] = os.path.join(self.deps_cpp_info["Python"].rootpath, self.deps_user_info["Python"].pyhome).replace("\\", "/")
        cmake.definitions["CONAN_PYTHON_INTERPRETER"] = os.path.join(self.deps_cpp_info["Python"].rootpath, self.deps_user_info["Python"].interpreter).replace("\\", "/")
        cmake.definitions["PYTHON_PATH_FOR_MODULES"] = os.path.join(self.deps_cpp_info["OpenTimelineIO"].rootpath, "python").replace("\\", "/")
        cmake.definitions["OTIO_SHARED_LIBRARY_DIR"] = os.path.join(self.deps_cpp_info["OpenTimelineIO"].rootpath, "python", "opentimelineio").replace("\\", "/")
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
