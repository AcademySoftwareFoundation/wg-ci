# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import environ, path
from conans import ConanFile, tools
from conans.tools import Git, Version
from conans.errors import ConanException

from jinja2 import Template
from os import path, makedirs


class QtSingleApplicationConan(ConanFile):
    name = "QtSingleApplication"
    description = "The QtSingleApplication component provides support for applications that can be only started once per user."
    url = "https://github.com/qtproject/qt-solutions"
    settings = "os", "compiler", "build_type", "arch"

    requires = ["Qt/5.15.2"]

    no_copy_source = False
    exports_sources = ["*.cmake.in"]

    author = "The Qt Company"
    license = "BSD-3-Clause"

    revision_mode = "scm"
    package_originator = "External"
    package_exportable = True


    @property
    def _useFoundryGLBackend(self):
        try: # If Qt is built with default GLBackend options this option is not present.
            return self.options["Qt"].GLBackend == "FoundryGL"
        except ConanException:
            return False

    @property
    def _source_dir(self):
        return f'{self.name}_src'


    @property
    def qtsingleapp_dir(self):
        return path.join(self.build_folder, f'{self.name}_src', 'qtsingleapplication')

    def requirements(self):
        if self._useFoundryGLBackend:
            self.requires("foundrygl/0.1@common/development")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = Git(folder=self._source_dir)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        qt_info = self.deps_cpp_info["Qt"]
        qt_bin_path = qt_info.bin_paths[0]
        qmake_path = path.join(qt_bin_path, "qmake")
        if self._useFoundryGLBackend:
          environ["FOUNDRYGL_FRAMEWORK_PATH"] = path.join( self.deps_cpp_info["foundrygl"].rootpath, "lib")
        with tools.chdir(self.qtsingleapp_dir):
            if self.settings.os == "Windows":
                self.run('configure.bat -library' )
            else:
                self.run('./configure -library' )
            pro_file = path.join('buildlib', 'buildlib.pro')
            self.run(f'{qmake_path} {pro_file}')
            if self.settings.os == "Windows":
                self.run('nmake')
            else:
                self.run(f'make -j {tools.cpu_count()}')

    def _produce_config_files(self):
        p = path.join(self.package_folder, "cmake")
        makedirs(p, exist_ok=True)

        ver = Version(self.version)

        def _configure(file_name):
            data = {
                "version_major": ver.major,
                "version_minor": ver.minor,
                "version_patch": ver.patch,
                "os": self.settings.os,
                "sh_suffix": ".so" if self.settings.os == "Linux" else ".dylib",
                "bt_suffix": "d" if self.settings.build_type == "Debug" else "",
            }

            with open(path.join(self.source_folder, file_name + ".in")) as file_:
                f = file_.read()
                template = Template(f)
            template.stream(data).dump(path.join(self.package_folder, "cmake", file_name))

        _configure("QtSingleApplicationConfig.cmake")
        _configure("QtSingleApplicationConfigVersion.cmake")

    def package(self):
        self.copy(pattern="*.h", dst='include/QtSingleApplication', src=path.join(self.qtsingleapp_dir, 'src'))
        self.copy(pattern="*.dll", dst='lib', src=path.join(self.qtsingleapp_dir, 'lib'), symlinks=True)
        self.copy(pattern="*.lib", dst='lib', src=path.join(self.qtsingleapp_dir, 'lib'), symlinks=True)
        self.copy(pattern="*.so*", dst='lib', src=path.join(self.qtsingleapp_dir, 'lib'), symlinks=True)
        self.copy(pattern="*.dylib", dst='lib', src=path.join(self.qtsingleapp_dir, 'lib'), symlinks=True)
        self._produce_config_files()
