# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import glob
import os
import shutil
from conans import ConanFile, CMake, tools


class OpenSubdivConan(ConanFile):
    name = "OpenSubdiv"
    license = "Apache-2.0"
    author = "Pixar"
    url = "http://graphics.pixar.com/opensubdiv/docs/intro.html"
    description = "OpenSubdiv is a set of open source libraries that implement high performance subdivision surface (subdiv) evaluation on massively parallel CPU and GPU architectures."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [False], # CMake scripts builds static only on Windows, but both on *nix; so using lowest common denominator
        "GLBackend": ["OpenGL" ,"FoundryGL"],
    }
    default_options = {
        "shared": False,
        "GLBackend": "OpenGL",
    }
    exports_sources = "cmake/*"
    no_copy_source = True
    generators = "cmake_paths"

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    requires = "GLEW/1.13.0@thirdparty/development"

    @property
    def _useFoundryGLBackend(self):
        return self.options.GLBackend == "FoundryGL"

    @property
    def _useOpenGLBackend(self):
        return self.options.GLBackend == "OpenGL"

    @property
    def _checkout_folder(self):
        return "{}_src".format(self.name)

    @property
    def _run_unit_tests(self):
        return "OPENSUBDIV_RUN_UNITTESTS" in os.environ

    def build_requirements(self):
        if self._useFoundryGLBackend:
            self.build_requires("foundrygl/0.1@common/development")

    def configure(self):
        # If using the non-default OpenGL backend then set on the dependent packages
        if not self._useOpenGLBackend:
            self.options["GLEW"].GLBackend = self.options.GLBackend

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_OpenSubdiv_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["GLEW_LOCATION"] = self.deps_cpp_info['GLEW'].rootpath # this is only necessary because of the NO_DEFAULT_PATH in the FindGLEW.cmake provided for non-Windows

        cmake.definitions["NO_LIB"] = "OFF"
        cmake.definitions["NO_EXAMPLES"] = "ON"
        cmake.definitions["NO_TUTORIALS"] = "ON"
        cmake.definitions["NO_REGRESSION"] = "OFF" if self._run_unit_tests else "ON"
        cmake.definitions["NO_PTEX"] = "ON"
        cmake.definitions["NO_DOC"] = "ON"
        cmake.definitions["NO_OMP"] = "ON"
        cmake.definitions["NO_TBB"] = "ON"
        cmake.definitions["NO_CUDA"] = "ON"
        cmake.definitions["NO_OPENCL"] = "ON"
        cmake.definitions["NO_CLEW"] = "ON"
        cmake.definitions["NO_OPENGL"] = "OFF"
        cmake.definitions["NO_METAL"] = "OFF" if self.settings.os == "Macos" else "ON"
        cmake.definitions["NO_DX"] = "ON"
        cmake.definitions["NO_TESTS"] = "OFF" if self._run_unit_tests else "ON"
        cmake.definitions["NO_GLTESTS"] = "ON"
        cmake.definitions["NO_GLFW"] = "ON"
        cmake.definitions["NO_GLFW_X11"] = "ON"
        cmake.definitions["OPENSUBDIV_GREGORY_EVAL_TRUE_DERIVATIVES"] = "OFF"

        if not self.options.shared:
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        cmake.configure(source_folder=os.path.join(self.source_folder, self._checkout_folder))
        return cmake

    def _remove_files_by_mask(self, directory, pattern):
        # not sure why tools.remove_files_by_mask is not working, for conan >= 1.26
        for filepath in glob.glob(os.path.join(directory, pattern)):
            os.unlink(filepath)

    def _remove_framework(self, framework_dir):
        if not os.path.isdir(framework_dir):
            return
        shutil.rmtree(framework_dir)

    def _write_cmake_config_version_file(self):
        tokens = {"OPENSUBDIV_VERSION": self.version}

        config_in_path = os.path.join(self.source_folder, "cmake", "OpenSubdivConfigVersion.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(config_out_dir, "OpenSubdivConfigVersion.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self._run_unit_tests:
            cmake.test()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("*.cmake", src="cmake", dst="cmake")
        self._write_cmake_config_version_file()
        if not self.options.shared:
            # remove shared library builds
            if self.settings.os == "Linux":
                self._remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so*")
            elif self.settings.os == "Macos":
                self._remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.dylib")
                self._remove_framework(os.path.join(self.package_folder, "lib", "OpenSubdiv.framework"))

    def package_info(self):
        pass # TODO: no tests for these yet
