# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools
import os, shutil
from jinja2 import Template


class PortAudioConan( ConanFile ):
    name = "PortAudio"
    author = "PortAudio team"
    description = "PortAudio is a cross-platform, open-source C language library for real-time audio input and output."
    license = "MIT"
    homepage = "https://www.portaudio.com/"
    url = "https://github.com/PortAudio/portaudio"
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    revision_mode = 'scm'
    package_originator = 'External'
    package_exportable = True
    generators = "cmake_paths"
    exports_sources = ["PortAudioConfig.cmake.in"]

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, f'{self.name}_src')

    @property
    def _should_run_unit_tests(self):
        return "PORTAUDIO_RUN_UNITTESTS" in os.environ

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def configure(self):
        del self.settings.compiler.libcxx

    def _configure_make(self, build_tests: bool = False):
        cmake = CMake(self)

        if build_tests or self._should_run_unit_tests:
            cmake.definitions['PA_BUILD_TESTS'] = 'ON'

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.definitions["PA_BUILD_SHARED"] = self.options.shared
        cmake.definitions["PA_BUILD_STATIC"] = not self.options.shared
        cmake.definitions['PA_ENABLE_DEBUG_OUTPUT'] = self.settings.build_type == 'Debug'
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_make()
        cmake.build()

    def test(self):
        cmake = self._configure_cmake(build_tests=True)
        cmake.test()

    def _produce_config_files(self):
        destination = os.path.join(self.package_folder, "cmake")
        os.makedirs(destination, exist_ok=True)

        def _configure(file_name):
            data = {
                "os": self.settings.os,
                "static": not self.options.shared,
            }

            with open(os.path.join(self.source_folder, file_name + ".in")) as file_:
                f = file_.read()
                template = Template(f)
            template.stream(data).dump(os.path.join(destination, file_name))

        _configure("PortAudioConfig.cmake")

    def package(self):
        cmake = self._configure_make()
        cmake.install()
        shutil.rmtree(os.path.join(self.package_folder, "lib", "cmake"))
        self._produce_config_files()
