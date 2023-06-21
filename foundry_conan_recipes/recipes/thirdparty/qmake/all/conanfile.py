# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conan import ConanFile
from conans import tools

from os import path, pathsep


class QMake(ConanFile):
    name = 'qmake'
    author = "The Qt Team"
    description = "The QMake tool for the Qt Project"
    license = 'LGPL-2.1-or-later'
    url = 'https://www.qt.io'
    package_originator = 'External'
    package_exportable = True

    settings = ['os', 'arch']
    revision_mode = 'scm'

    build_requires = ['Perl/[~5]']


    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _perl_lib(self):
        perl_lib = None
        if self.settings.os == 'Linux':
            perl_ver = tools.Version(self.deps_cpp_info['Perl'].version)
            base_lib = path.join(self.deps_cpp_info['Perl'].rootpath, 'lib', f'perl{perl_ver.major}', f'{perl_ver}')
            perl_lib = pathsep.join([base_lib, path.join(base_lib, "x86_64-linux")])
        return perl_lib


    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

        perl_dir = path.join(self.deps_cpp_info['Perl'].rootpath, 'bin')
        perl = path.join(perl_dir, 'perl')
        src_dir = path.join(self.source_folder, self._source_subfolder)

        with tools.environment_append({"PERLLIB": self._perl_lib}):
            self.run(
                f'{perl} init-repository --module-subset=qtbase',
                    cwd=src_dir,
                    run_environment=True,
            )

    def build(self):
        config_args = [
            '-silent',
            '-c++std', 'c++14',
            '-confirm-license',
            '-opensource',
            '-prefix', self.package_folder,
            '-shared',
        ]
        config_args_str = " ".join(config_args)

        src_dir = path.join(self.source_folder, self._source_subfolder)
        if self.settings.os == 'Windows':
            self.run(
                path.join(
                    src_dir,
                    f'configure.bat {config_args_str}'
                ), run_environment=True
            )
        else:
            with tools.environment_append({"PERLLIB": self._perl_lib}):
                self.run(
                    path.join(
                        src_dir,
                        f'configure {config_args_str}'
                    ), run_environment=True
                )

    def package(self):
        self.copy('*', src='qtbase/bin', dst='bin')
        self.copy('*', src=f'{self._source_subfolder}/qtbase/mkspecs', dst='mkspecs')
        self.copy('*', src=f'qtbase/mkspecs', dst='mkspecs')

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bindir = path.join(self.package_folder, 'bin')
        self.env_info.PATH.append(bindir)
