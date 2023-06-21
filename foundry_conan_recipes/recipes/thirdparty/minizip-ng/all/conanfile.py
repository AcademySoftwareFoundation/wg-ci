# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, tools, CMake


class MinizipNGConan(ConanFile):
    name = 'minizip-ng'
    license = 'Zlib'
    author = 'Nathan Moinvaziri'
    description = 'Fork of the popular zip manipulation library found in the zlib distribution.'
    url = 'https://github.com/zlib-ng/minizip-ng'

    settings = 'os', 'arch', 'compiler', 'build_type'

    options = {'shared': [False], 'fPIC': [True, False], 'compat': [True, False]}
    default_options = {'shared': False, 'fPIC': True, 'compat': True}

    revision_mode = 'scm'
    package_originator = 'External'
    package_exportable = True

    requires = ('zlib/1.2.13', )

    @property
    def _checkout_subfolder(self):
        return f'{self.name}_src'

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._checkout_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def _configure_cmake(self):
        cmake = CMake(self)
        # Note that CMAKE_PROJECT_minizip_INCLUDE cannot be used because the project name in
        # the minizip's main CMake file is defined *after* packages have been required.
        cmake.definitions['CMAKE_PREFIX_PATH'] = self.deps_cpp_info['zlib'].rootpath

        cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
        cmake.definitions['CMAKE_CXX_VISIBILITY_PRESET'] = 'hidden'
        cmake.definitions['CMAKE_VISIBILITY_INLINES_HIDDEN'] = 'ON'

        # If enabled (default), the library will be named 'minizip' (and not 'minizip-ng'), which
        # also affects the CMake targets, as well as availability of the legacy header files.
        cmake.definitions['MZ_COMPAT'] = self.options.compat

        cmake.definitions['MZ_FETCH_LIBS'] = False  # Do not allow fetching external libraries
        cmake.definitions['MZ_BCRYPT'] = False
        cmake.definitions['MZ_BZIP2'] = False
        cmake.definitions['MZ_ICONV'] = False
        cmake.definitions['MZ_LIBBSD'] = False
        cmake.definitions['MZ_LIBCOMP'] = False
        cmake.definitions['MZ_LZMA'] = False
        cmake.definitions['MZ_OPENSSL'] = False
        cmake.definitions['MZ_PKCRYPT'] = False
        cmake.definitions['MZ_SIGNING'] = False
        cmake.definitions['MZ_WZAES'] = False
        cmake.definitions['MZ_ZSTD'] = False

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        cmake.configure(source_dir=self._checkout_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
