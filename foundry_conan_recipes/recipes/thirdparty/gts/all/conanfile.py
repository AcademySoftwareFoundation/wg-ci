# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools
from jinja2 import Environment, FileSystemLoader


class GTSConan(ConanFile):
    name = "GTS"
    license = "LGPL-2.0-only"
    author = "Stéphane Popinet"
    url = "https://gts.sourceforge.net"
    description = ("GTS stands for the GNU Triangulated Surface Library. It is an Open Source Free "
                   "Software Library intended to provide a set of useful functions to deal with 3D "
                   "surfaces meshed with interconnected triangles.")
    settings = "os", "compiler", "build_type", "arch"

    options = {"shared": [True]}
    default_options = {"shared": True}

    exports_sources = "cmake/*"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    requires = ('GLib/2.75.2', )

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if self.settings.os == 'Macos':
            self.build_requires('pkgconfig/0.29.2@thirdparty/development')

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        glib_rootpath = self.deps_cpp_info['GLib'].rootpath
        glib_include_dir = os.path.join(glib_rootpath, 'include')
        glib_lib_dir = os.path.join(glib_rootpath, 'lib')

        if self.settings.os == "Windows":
            glib_lib_filepath = os.path.join(glib_lib_dir, 'glib-2.0.lib')
            glib_include_glib_dir = os.path.join(glib_include_dir, 'glib-2.0')
            glib_lib_include_dir = os.path.join(glib_lib_dir, 'glib-2.0', 'include')

            env = {}
            env['EXTRA_CFLAGS'] = '-Od' if self.settings.build_type == 'Debug' else '-Ox'
            env['EXTRA_CFLAGS'] += (f' -I "{os.path.normpath(glib_include_dir)}" '
                                    f'-I "{os.path.normpath(glib_include_glib_dir)}" '
                                    f'-I "{os.path.normpath(glib_lib_include_dir)}" ')
            env['EXTRA_LINK_FLAGS'] = f'"{os.path.normpath(glib_lib_filepath)}"'

            with tools.environment_append(env):
                with tools.chdir(os.path.join(self._source_subfolder, 'src')):
                    self.run('nmake -f makefile.msc all')
        else:
            glib_pkgconfig_dir = os.path.join(glib_lib_dir, 'pkgconfig')

            env = {}
            env['PKG_CONFIG_PATH'] = [glib_pkgconfig_dir]

            if self.settings.os == 'Linux':
                env['LD_LIBRARY_PATH'] = [glib_lib_dir]
                # pkg-config is assumed installed on Linux machines.
            elif self.settings.os == 'Macos':
                env['DYLD_LIBRARY_PATH'] = [glib_lib_dir]
                env['PATH'] = [self.deps_cpp_info["pkgconfig"].bin_paths[0]]

            with tools.environment_append(env), tools.chdir(self._source_subfolder):
                os.chmod('configure', 0o775)

                autotools = AutoToolsBuildEnvironment(self)
                args = ["--enable-shared", "--disable-static"]
                autotools.configure(args=args)
                autotools.make()
                autotools.install()

    def package(self):
        if self.settings.os == "Windows":
            src = os.path.join(self._source_subfolder, 'src')
            self.copy(pattern='gts-*.lib', dst='lib', src=src, keep_path=False)
            self.copy(pattern='gts-*.dll', dst='lib', src=src, keep_path=False)
            self.copy(pattern='gts-*.pdb', dst='lib', src=src, keep_path=False)
            self.copy(pattern='gts.h', dst='include', src=src, keep_path=False)
            self.copy(pattern='gtsconfig.h', dst='include', src=src, keep_path=False)
        else:
            # As part of the build stage.
            pass

        self._write_cmake_config_files()

    def _write_cmake_config_files(self):
        cmake_dst = os.path.join(self.package_folder, 'cmake')
        os.makedirs(cmake_dst, exist_ok=True)

        if self.settings.os == 'Windows':
            lib_dirname = 'lib'
            lib_prefix = ''
            lib_suffix = f'-{tools.Version(self.version).major}.{tools.Version(self.version).minor}'
            lib_extension = '.dll'
        else:
            lib_dirname = 'lib'
            lib_prefix = 'lib'
            lib_suffix = ''
            lib_extension = '.so' if self.settings.os == 'Linux' else '.dylib'

        data = {
            'os': self.settings.os,
            'lib_version': str(self.version),
            'lib_dirname': lib_dirname,
            'lib_filename': f'{lib_prefix}gts{lib_suffix}{lib_extension}',
        }

        if self.settings.os == 'Windows':
            data['win_lib_filename'] = f'gts{lib_suffix}.lib'

        file_loader = FileSystemLoader(os.path.join(self.source_folder, 'cmake'))
        env = Environment(loader=file_loader)

        cmakeconfig_template = env.get_template('GTSConfig.cmake.in')
        cmakeconfig_template.stream(data).dump(os.path.join(cmake_dst, 'GTSConfig.cmake'))

        cmakeconfigversion_template = env.get_template('GTSConfigVersion.cmake.in')
        cmakeconfigversion_template.stream(data).dump(
            os.path.join(cmake_dst, 'GTSConfigVersion.cmake'))
