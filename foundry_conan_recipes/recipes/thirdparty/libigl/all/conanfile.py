# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil

from conans import ConanFile, CMake, tools
from jinja2 import Environment, FileSystemLoader


class LibIglConan(ConanFile):
    name = 'libigl'
    description = 'A simple C++ geometry processing library.'
    url = 'https://libigl.github.io/'
    license = 'MPL-2.0'
    author = 'Alec Jacobson and Daniele Panozzo and others'

    settings = 'os', 'arch', 'compiler', 'build_type'
    options = {'shared': [False], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    exports_sources = '*cmake.in'
    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    def requirements(self):
        self.requires('eigen/3.4.0@')

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy('*.a', 'lib', 'lib')
        self.copy('*.lib', 'lib', 'lib')

        include_src = os.path.join(self.build_folder, self._source_subfolder, 'include', 'igl')
        include_dst = os.path.join(self.package_folder, 'include', 'igl')
        os.makedirs(include_dst, exist_ok=True)

        for item in os.listdir(include_src):
            item_path = os.path.join(include_src, item)
            if os.path.isfile(item_path) and os.path.splitext(item_path)[1] == '.h':
                shutil.copy2(item_path, include_dst)

        self._write_cmake_config_file()

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'

    def _configure_cmake(self):
        cmake = CMake(self)

        if not self.options.shared:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_CXX_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_VISIBILITY_INLINES_HIDDEN'] = 'ON'

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        # Don't build tests and tutorials.
        cmake.definitions['LIBIGL_BUILD_TESTS'] = 'OFF'
        cmake.definitions['LIBIGL_BUILD_TUTORIALS'] = 'OFF'

        # Don't perform an install as to ensure that copyleft headers are excluded.
        cmake.definitions['LIBIGL_INSTALL'] = 'OFF'

        # This library is provided as header-only or via a static library.
        cmake.definitions['LIBIGL_USE_STATIC_LIBRARY'] = 'ON'

        # Permissive modules. These modules are available under MPL2 license, and their dependencies
        # are available under a permissive or public domain license.
        cmake.definitions['LIBIGL_EMBREE'] = 'OFF'
        cmake.definitions['LIBIGL_GLFW'] = 'OFF'
        cmake.definitions['LIBIGL_IMGUI'] = 'OFF'
        cmake.definitions['LIBIGL_OPENGL'] = 'OFF'
        cmake.definitions['LIBIGL_PNG'] = 'OFF'
        cmake.definitions['LIBIGL_PREDICATES'] = 'OFF'
        cmake.definitions['LIBIGL_XML'] = 'OFF'

        # Copyleft modules. These modules are available under GPL license, and their dependencies are
        # available under a copyleft license.
        cmake.definitions['LIBIGL_COPYLEFT_CORE'] = 'OFF'
        cmake.definitions['LIBIGL_COPYLEFT_CGAL'] = 'OFF'
        cmake.definitions['LIBIGL_COPYLEFT_COMISO'] = 'OFF'
        cmake.definitions['LIBIGL_COPYLEFT_TETGEN'] = 'OFF'

        cmake.definitions['LIBIGL_RESTRICTED_MATLAB'] = 'OFF'
        cmake.definitions['LIBIGL_RESTRICTED_MOSEK'] = 'OFF'
        cmake.definitions['LIBIGL_RESTRICTED_TRIANGLE'] = 'OFF'

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))

        return cmake

    def _write_cmake_config_file(self):
        p = os.path.join(self.package_folder, 'cmake')
        if not os.path.exists(p):
            os.mkdir(p)

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {
                'libprefix' : '' if self.settings.os == 'Windows' else 'lib',
                'libsuffix' : 'lib' if self.settings.os == 'Windows' else 'a'
            }

            interpreter_template = env.get_template(file_name + '.in')
            interpreter_template.stream(data).dump(os.path.join(self.package_folder, 'cmake', file_name))

        _configure('IglConfig.cmake')
