# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
import shutil
from conans import ConanFile, CMake, tools

class FreetypeConan(ConanFile):
    name = "Freetype"
    license = "FTL"
    url = "https://www.freetype.org/"
    description = "Freetype is a freely available software library to render fonts."
    author = "David Turner, Robert Wilhelm, and Werner Lemberg"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = { "shared": False, "fPIC": True }
    generators = "cmake_paths"
    revision_mode = "scm"
   
    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _run_unit_tests(self):
        return "FREETYPE_RUN_UNITTESTS" in os.environ

    def source(self):
        git = tools.Git(folder=self._source_subfolder)
        version_data = self.conan_data["sources"][self.version]
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_BrotliDec"] = "TRUE"   # See issue #88.
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_BZip2"] = "TRUE"
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_HarfBuzz"] = "TRUE"   # See issue #88.
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_PNG"] = "TRUE"
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_ZLIB"] = "TRUE"
        cmake.definitions["DISABLE_FORCE_DEBUG_POSTFIX"] = "TRUE"

        cmake.definitions["CMAKE_PROJECT_freetype_INCLUDE"] = path.join(self.install_folder, "conan_paths.cmake")
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        # disable all RPATHs so that build machine paths do not appear in binaries
        cmake.definitions["CMAKE_SKIP_RPATH"] = "1"

        cmake.configure(
            source_folder = path.join(self.source_folder, self._source_subfolder)
        )
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        # Beware: the build-provided cmake files are deleted, because later versions of Freetype do not conform to the Freetype documentation (https://cmake.org/cmake/help/latest/module/FindFreetype.html). The documentation requires Freetype to be in a namespace, as per modern cmake. The >=v2.10.2 versions of Freetype do not appear to generate such conforming cmake-files.
        shutil.rmtree(path.join(self.package_folder, "lib", "cmake"))
  
    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["freetype.lib"]
        else:
            self.cpp_info.libs = ["freetype"]
