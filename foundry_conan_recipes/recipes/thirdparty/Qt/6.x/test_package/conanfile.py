# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake
from conans.errors import ConanException

class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake_paths"

    @property
    def _useFoundryGLBackend(self):
        try:
            return self.options["Qt"].GLBackend == "FoundryGL"
        except ConanException:
            return False

    def requirements(self):
        if self._useFoundryGLBackend:
            self.requires("foundrygl/0.1@common/development")

    def imports(self):
        if self.settings.os == "Windows":
            self.copy("*", keep_path=True)

        if self._useFoundryGLBackend:
            self.copy("*", src="lib", root_package="foundrygl", keep_path=True)

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(self.install_folder, "conan_paths.cmake")
        unescaped_path = path.join(self.source_folder, "spheres.svg")
        cmake.definitions["CMAKE_SVG_IMAGE_FILEPATH"] = unescaped_path.replace("\\", "/") if self.settings.os == "Windows" else unescaped_path
        unescaped_path = path.join(self.source_folder, "JPG_Test.jpeg")
        cmake.definitions["CMAKE_JPEG_IMAGE_FILEPATH"] = unescaped_path.replace("\\", "/") if self.settings.os == "Windows" else unescaped_path
        unescaped_path = path.join(self.source_folder, "z09n2c08.png")
        cmake.definitions["CMAKE_PNG_IMAGE_FILEPATH"] = unescaped_path.replace("\\", "/") if self.settings.os == "Windows" else unescaped_path
        unescaped_path = path.join(self.source_folder, "QML_main.qml")
        cmake.definitions["CMAKE_QML_main_FILEPATH"] = unescaped_path.replace("\\", "/") if self.settings.os == "Windows" else unescaped_path
        unescaped_path = path.join(self.source_folder, "QGraphicalEffects_main.qml")
        cmake.definitions["CMAKE_QGraphicalEffects_main_FILEPATH"] = unescaped_path.replace("\\", "/") if self.settings.os == "Windows" else unescaped_path
        unescaped_path = path.join(self.source_folder, "QQuick_main.qml")
        cmake.definitions["CMAKE_QQuick_main_FILEPATH"] = unescaped_path.replace("\\", "/") if self.settings.os == "Windows" else unescaped_path
        cmake.definitions["INCLUDES_WEBENGINE"] = self.options["Qt"].with_webengine
        cmake.configure()
        cmake.build()
        cmake.parallel=False
        cmake.test(output_on_failure=True)
