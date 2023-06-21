# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, RunEnvironment, tools


class QtConan(ConanFile):
    name = 'Qt'
    license = 'LGPL-2.1-or-later'
    author = 'The Qt Team'
    url = 'https://www.qt.io'
    description = 'Everything you need for your entire software development life cycle. Qt is the fastest and smartest way to produce industry-leading software that users love.'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True], 'with_webengine':[True,False], 'with_vulkan':[True,False], "GLBackend": ["OpenGL" ,"FoundryGL"]}
    default_options = {'shared': True, 'with_webengine': False, 'with_vulkan': False, "GLBackend": "OpenGL"}
    generators = 'cmake_paths'
    short_paths = True

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _useFoundryGLBackend(self):
        return self.options.GLBackend == "FoundryGL"

    build_requires = [
        'JPEG/9e',
        'OpenSSL/[~1.1.1m]',
        'Perl/[~5]',
        'Python/[~3.9.10]', # WebEngine requires Python >=3.x, QML requires Python >=2.x
        'PNG/[~1.6.37]@thirdparty/development',
        'SQLite/3.32.3@thirdparty/development',
        'libtiff/4.3.0',
    ]

    def requirements(self):
        if self._useFoundryGLBackend:
            self.requires("foundrygl/0.1@common/development")

    def build_requirements(self):
        if self.options.with_webengine:
            self.build_requires('nodejs/18.4.0@thirdparty/testing')
        if self.options.with_vulkan:
            self.build_requires('Vulkan/1.2.176.1@thirdparty/development')

    @property
    def _excluded_inputs(self):
        unrequired_inputs = [
            'cups',
            'eglfs',
            'icu',
            'mtdev',
            'openvg',
            'pch',
            'sql_db2',
            'sql_ibase',
            'sql_mysql',
        ]
        return unrequired_inputs

    @property
    def _excluded_modules(self):
        # see https://www.qt.io/product/features#js-6-3
        # exclude all GPL-only licensed modules
        gpl_modules = [
            'qtcharts',
            'qtdatavis3d',
            'qtlottie',
            'qtnetworkauth',
            'qtqa',
            'qtquick3d',
            'qtquicktimeline',
            'qtvirtualkeyboard',
            'qtwayland',
            'qtwebglplugin',
        ]
        excluded = [
            'qtactiveqt',
            'qtconnectivity',
            'qtdoc',
            'qtgamepad',
            'qtpurchasing',
            'qtspeech',
            'qtwebsockets',
            'qtwebview'
        ]
        if not self.options.with_webengine:
            excluded.append('qtwebengine')
        excluded.extend(gpl_modules)
        return excluded

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])
        perl_dir = os.path.join(self.deps_cpp_info["Perl"].rootpath, "bin")
        perl = os.path.join(perl_dir, "perl")
        src_dir = os.path.join(self.source_folder, self._source_subfolder)

        # not all modules in Qt are desired/needed, so exclude them from the source checkout (i.e. their submodules are not populated)
        module_subset = self._excluded_modules
        module_subset_expr = "--module-subset=default," + ",".join(f"-{module}" for module in module_subset)
        self.run(f"{perl} init-repository {module_subset_expr}", cwd=src_dir)

    def _environment(self):
        env = RunEnvironment(self).vars

        if self.options.with_vulkan:
            env['VULKAN_SDK'] = os.path.dirname(self.deps_cpp_info['Vulkan'].lib_paths[0])

        return env

    @property
    def _is_multi_configuration(self):
        return self.settings.os == 'Macos' and self.settings.build_type == 'Debug'

    def _setup_cmake(self):
        build_type = "RelWithDebInfo"       if self.settings.build_type == 'Release' \
                     else None # None = use default
        generator  = "Ninja Multi-Config"   if self._is_multi_configuration \
                     else None # None = use default

        cmake = CMake(self, generator=generator, build_type=build_type)

        # The CMake equivalent of the configure options is documented at:
        # https://github.com/qt/qtbase/blob/dev/cmake/configure-cmake-mapping.md

        if self.settings.os == 'Macos':
            cmake.definitions['FEATURE_framework'] = 'ON'
            if self.settings.build_type == 'Debug':
                cmake.definitions['CMAKE_CONFIGURATION_TYPES'] = "Release;Debug"

        cmake.definitions['BUILD_SHARED_LIBS'] = 'ON' if self.options.shared else 'OFF'
        cmake.definitions['QT_BUILD_EXAMPLES'] = 'OFF'
        cmake.definitions['QT_BUILD_TESTS'] = 'OFF'

        cmake.definitions['FEATURE_gif'] = 'ON'
        cmake.definitions['FEATURE_harfbuzz'] = 'ON'
        cmake.definitions['FEATURE_system_harfbuzz'] = 'OFF'
        cmake.definitions['FEATURE_ico'] = 'ON'
        cmake.definitions['FEATURE_pcre2'] = 'ON'
        cmake.definitions['FEATURE_system_pcre2'] = 'OFF'
        cmake.definitions['FEATURE_libjpeg'] = 'ON'
        cmake.definitions['FEATURE_system_libjpeg'] = 'ON'
        cmake.definitions['FEATURE_libpng'] = 'ON'
        cmake.definitions['FEATURE_system_libpng'] = 'ON'
        cmake.definitions['FEATURE_vulkan'] = 'ON' if self.options.with_vulkan else 'OFF'
        cmake.definitions['FEATURE_zlib'] = 'ON'
        cmake.definitions['FEATURE_system_zlib'] = 'ON'

        for module in self._excluded_modules:
            cmake.definitions[f'BUILD_{module}'] = 'OFF'

        for input in self._excluded_inputs:
            cmake.definitions[f'INPUT_{input}'] = 'OFF'

        cmake.definitions['INPUT_opengl'] = 'desktop'
        cmake.definitions['INPUT_openssl'] = 'yes'

        cmake.definitions['CMAKE_PROJECT_Qt_INCLUDE'] = os.path.join(self.install_folder, 'conan_paths.cmake')
        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        # min requires 10.15 SDK on macOSX (Xcode11)
        with tools.environment_append(self._environment()):
            cmake = self._setup_cmake()

            if self._is_multi_configuration:
                cmake.build(['--config=Debug'])
                cmake.build(['--config=Release'])
            else:
                cmake.build()

    def package(self):
        with tools.environment_append(self._environment()):
            if self._is_multi_configuration:
                self.run(f'cmake --install {self.build_folder} --prefix {self.package_folder} --config=Debug')
                self.run(f'cmake --install {self.build_folder} --prefix {self.package_folder} --config=Release')
            else:
                self.run(f'cmake --install {self.build_folder} --prefix {self.package_folder}')

        # add qt.conf file to make the package relocatable
        bin_folder = os.path.join(self.package_folder, "bin")
        os.makedirs(bin_folder, exist_ok=True)
        with open(os.path.join(bin_folder, "qt.conf"), "wt") as conf_file:
            conf_file.writelines(["[Paths]\n", "Prefix = ..\n"])
