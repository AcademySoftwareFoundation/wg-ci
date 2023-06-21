# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanException


class AbseilConan(ConanFile):
    name = 'abseil'
    license = 'Apache-2.0'
    author = "Google Inc"
    url = 'https://github.com/abseil/abseil-cpp'
    description = 'Abseil is an open-source collection of C++ code ' \
                  '(compliant to C++11) designed to augment the C++ ' \
                  'standard library.'

    settings = 'os', 'compiler', 'build_type', 'arch'

    options = {'shared': [False], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, '{}_src'.format(self.name))

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        cmake = CMake(self)

        if not self.options.shared:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_CXX_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_VISIBILITY_INLINES_HIDDEN'] = 'ON'

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = \
                self.options.fPIC

        # Abseil requires at least C++11 (see absl/base/policy_checks.h).
        # If `CMAKE_CXX_STANDARD` is not set, the compiler's default C++
        # standard will be used. While this works fine with MSVC and GCC, where
        # the compiler's version is bound to a specific default C++ standard,
        # in macOS, the default C++ standard is C++98, which Abseil does not
        # support.
        cmake.definitions['CMAKE_CXX_STANDARD'] = 11

        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()
        # The CMake install target is a bit erratic, installing certain
        # `CMakeFiles/` temporary directories in multiple locations.
        # Instead, we will copy files in the `package()` function (as seen in
        # https://github.com/abseil/abseil-cpp/blob/master/conanfile.py).

    def package(self):
        self.copy('LICENSE', dst='licenses')
        self.copy('*.h', dst='include', src=self._source_subfolder)
        self.copy('*.inc', dst='include', src=self._source_subfolder)
        self.copy('*.a', dst='lib', src='.', keep_path=False)
        self.copy('*.lib', dst='lib', src='.', keep_path=False)

        # While the CMake install target would install files in
        # `./lib/cmake/absl/`, we expect CMake files in `./cmake/`.
        self.copy('abslConfig.cmake', dst='cmake')
        self.copy('*.cmake',
                  dst='cmake',
                  src='CMakeFiles/Export/lib/cmake/absl/',
                  keep_path=False)

        # Since CMake files are moved from `./lib/cmake/absl/` to `./cmake/`,
        # the targets' relative paths need to be adjusted.
        targets_filepath = '{}/cmake/abslTargets.cmake'.format(
            self.package_folder)
        for separator in ('\n', '\r\n'):
            # Basically, this line, that appears three consecutive times in the
            # original CMake file, needs to be tweaked, so that it only appears
            # once.
            line = ('get_filename_component(_IMPORT_PREFIX '
                    '"${{_IMPORT_PREFIX}}" PATH){}'.format(separator))
            try:
                tools.replace_in_file(targets_filepath, line + line + line,
                                      line)
                break
            except ConanException:
                continue
        else:
            raise RuntimeError('Unable to adjust relative path to targets.')

    def package_info(self):
        # As seen in https://github.com/abseil/abseil-cpp/blob/master/conanfile.py.
        if self.settings.os in ('Linux', 'Macos'):
            self.cpp_info.libs = ['-Wl,--start-group']
        self.cpp_info.libs.extend(tools.collect_libs(self))
        if self.settings.os in ('Linux', 'Macos'):
            self.cpp_info.libs.extend(['-Wl,--end-group', 'pthread'])
