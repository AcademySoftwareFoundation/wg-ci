# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil

from conans import ConanFile, CMake, tools


class OpenCVConan(ConanFile):
    name = 'OpenCV'
    license = 'BSD-3-Clause'
    author = 'OpenCV development team'
    url = 'https://github.com/opencv/opencv'
    description = 'OpenCV (Open Source Computer Vision Library) is an open ' \
                  'source computer vision and machine learning software ' \
                  'library.'

    settings = 'os', 'compiler', 'build_type', 'arch'

    options = {'shared': [True], 'fPIC': [True]}
    default_options = {'shared': True, 'fPIC': True}

    generators = "cmake_paths"

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    build_requires = ('zlib/1.2.11@thirdparty/development', )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        self.options['zlib'].shared = False

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, '{}_src'.format(self.name))

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def _configure_cmake(self):
        cmake = CMake(self)

        if not self.options.shared:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_CXX_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_VISIBILITY_INLINES_HIDDEN'] = True

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = \
                self.options.fPIC

        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared

        cmake.definitions['BUILD_EXAMPLES'] = False
        cmake.definitions['BUILD_DOCS'] = False
        cmake.definitions['BUILD_TESTS'] = False
        cmake.definitions['BUILD_PACKAGE'] = False
        cmake.definitions['BUILD_PERF_TESTS'] = False
        cmake.definitions['BUILD_ZLIB'] = False
        cmake.definitions['BUILD_JPEG'] = False
        cmake.definitions['BUILD_PNG'] = False
        cmake.definitions['BUILD_TIFF'] = False
        cmake.definitions['BUILD_JASPER'] = False
        cmake.definitions['BUILD_OPENEXR'] = False

        cmake.definitions['BUILD_opencv_python'] = False

        cmake.definitions['WITH_CUFFT'] = False
        cmake.definitions['WITH_CUBLAS'] = False
        cmake.definitions['WITH_NVCUVID'] = False
        cmake.definitions['WITH_FFMPEG'] = False
        cmake.definitions['WITH_GSTREAMER'] = False
        cmake.definitions['WITH_GTK'] = False
        cmake.definitions['WITH_OPENCL'] = False
        cmake.definitions['WITH_CUDA'] = False

        cmake.definitions['WITH_JPEG'] = False
        cmake.definitions['WITH_PNG'] = False
        cmake.definitions['WITH_TIFF'] = False
        cmake.definitions['WITH_JASPER'] = False
        cmake.definitions['WITH_OPENEXR'] = False
        cmake.definitions['WITH_EIGEN'] = False
        cmake.definitions['WITH_TBB'] = False

        # To prevent OpenCV's CMakeLists.txt from finding the system's
        # installation of zlib.
        cmake.definitions["CMAKE_PROJECT_OpenCV_INCLUDE"] = \
            os.path.join(self.install_folder, "conan_paths.cmake")

        cmake.configure(source_folder=self._source_subfolder)

        return cmake

    def build(self):
        self._configure_cmake().build()

    def package(self):
        self._configure_cmake().install()

        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

        # CMake files are written to some odd locations:
        #
        #   - Linux/macOS: ./share/OpenCV/
        #   - Windows:     ./ and ./x64/vc15/
        #
        # Also, binary files in Windows are written to equally odd places:
        #
        #   - Linux/macOS:        ./lib/ (expected)
        #   - Windows .lib files: ./x64/vc15/lib/
        #   - Windows .dll files: ./x64/vc15/bin/
        #
        # These files need to be relocated to more sensible places, and the
        # relative paths in the CMake files need to be adjusted accordingly.
        with tools.chdir(self.package_folder):
            if self.settings.os == 'Windows':
                self._reorganize_package_files_win()
            else:
                self._reorganize_package_files_unix()

    def _reorganize_package_files_unix(self):
        # Move `.cmake` files to the `cmake/` directory.
        tools.rmdir('cmake')
        os.mkdir('cmake')
        for file in os.listdir('share/OpenCV'):
            if file.endswith('.cmake'):
                shutil.move(os.path.join('share', 'OpenCV', file), 'cmake')

        # Fix up relative paths in CMake files.
        tools.replace_in_file(
            'cmake/OpenCVConfig.cmake',
            'set(OpenCV_INSTALL_PATH "${OpenCV_CONFIG_PATH}/../..")',
            'set(OpenCV_INSTALL_PATH "${OpenCV_CONFIG_PATH}/..")')
        tools.replace_in_file(
            'cmake/OpenCVModules.cmake',
            'get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)',
            '')
        tools.replace_in_file(
            'cmake/OpenCVModules.cmake',
            'get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)',
            'get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)\n'
            'get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)')

    def _reorganize_package_files_win(self):
        if tools.Version(self.settings.compiler.version) < "16":
            # Flatten directories containing the `.exe`, `.dll`, `.lib` files.
            arch_path = 'x64'
            vc_path = os.listdir(arch_path)[0]
            bin_path = os.path.join(arch_path, vc_path, 'bin')
            lib_path = os.path.join(arch_path, vc_path, 'lib')
            tools.rmdir('bin')
            tools.rmdir('lib')
            shutil.move(bin_path, 'bin')
            shutil.move(lib_path, 'lib')
            tools.rmdir(arch_path)

        # Move `.cmake` files to the `cmake/` directory.
        tools.rmdir('cmake')
        os.mkdir('cmake')
        os.mkdir('cmake/targets')
        shutil.move('OpenCVConfig.cmake', 'cmake')
        shutil.move('OpenCVConfig-version.cmake', 'cmake')
        for file in os.listdir('lib'):
            if file.endswith('.cmake'):
                shutil.move(os.path.join('lib', file), 'cmake/targets')

        # Fix up relative paths in CMake files.
        tools.replace_in_file(
            'cmake/OpenCVConfig.cmake', 'if(OpenCV_LIB_PATH AND EXISTS ',
            'set(OpenCV_LIB_PATH "${OpenCV_CONFIG_PATH}/../lib")\n'
            'if(OpenCV_LIB_PATH AND EXISTS ')
        tools.replace_in_file(
            'cmake/OpenCVConfig.cmake',
            '${OpenCV_LIB_PATH}/OpenCVConfig.cmake',
            '${OpenCV_CONFIG_PATH}/targets/OpenCVConfig.cmake')
        tools.replace_in_file('cmake/targets/OpenCVConfig.cmake',
                              '${OpenCV_CONFIG_PATH}/include',
                              '${OpenCV_CONFIG_PATH}/../include')
        tools.replace_in_file(
            'cmake/targets/OpenCVModules.cmake',
            'get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)',
            '')
        tools.replace_in_file(
            'cmake/targets/OpenCVModules.cmake',
            'get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)',
            'get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)\n'
            'get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)\n'
            'get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)\n'
        )
        if tools.Version(self.settings.compiler.version) < "16":
            tools.replace_in_file(
                'cmake/targets/OpenCVModules-{}.cmake'.format(
                    str(self.settings.build_type).lower()),
                arch_path + '/' + vc_path + '/', '')
