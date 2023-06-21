# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class JemallocConan(ConanFile):
    name = 'jemalloc'
    url = 'http://jemalloc.net'
    license = 'BSD-2-Clause'
    description = 'jemalloc is a general purpose malloc(3) implementation ' \
        'that emphasizes fragmentation avoidance and scalable concurrency ' \
        'support.'
    author = 'Jason Evans'

    settings = 'os', 'compiler', 'build_type', 'arch'

    options = {'shared': [True], 'fPIC': [True]}
    default_options = {'shared': True, 'fPIC': True}

    exports_sources = '*'

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git()
        git.clone(version_data['git_url'], 'master')
        git.checkout(version_data['git_hash'])

        if self.settings.os == 'Windows':
            # Cygwin is required with at least the following packages:
            #    * autoconf
            #    * autogen
            #    * gawk
            #    * grep
            #    * sed
            # See https://github.com/jemalloc/jemalloc/blob/dev/msvc/ReadMe.txt.
            #
            # Since the VM may not feature Cygwin, an standalone archive will
            # be downloaded.
            git = tools.Git(folder='cygwin-standalone')
            git.clone(
                'git@a_gitlab_url:libraries/conan/thirdparty/cygwin-standalone.git',
                branch='foundry/v3.3.4')
            tools.untargz('cygwin-standalone/cygwin64.tgz')

    def build(self):
        args = [
            '--with-jemalloc-prefix=je_',
            '--disable-cxx',
            '--disable-prof-libgcc',
            '--disable-prof-gcc',
            '--disable-initial-exec-tls',
        ]
        if self.settings.build_type == 'Release':
            args.append('--disable-stats')
            args.append('--disable-fill')
        if self.settings.build_type == 'Debug':
            args.append('--enable-debug')

        if self.settings.os == 'Linux':
            with tools.chdir(self.source_folder):
                self.run('autoconf')
            autoconf = AutoToolsBuildEnvironment(self)
            autoconf.configure(configure_dir=self.source_folder, args=args)
            autoconf.make()
            autoconf.install(args=['-j1'])

        elif self.settings.os == 'Windows':
            build_folder = os.path.normpath(self.build_folder)
            build_folder = build_folder.replace('\\', '/')
            args.append('--prefix=\\"{}\\"'.format(build_folder))
            with tools.chdir(self.source_folder):
                cygwin_dir = \
                    os.path.join(self.source_folder, 'cygwin64', 'bin')
                with tools.environment_append({'PATH': [cygwin_dir]}):
                    self.run('sh -c "CC=cl ./autogen.sh {}"'.format(
                        ' '.join(args)))
                known_toolchains = {
                    "15": "v141",  # VS 2017.
                    "16": "v142",  # VS 2019.
                    "17": "v143",  # VS 2022.
                }
                self.run(
                    'msbuild msvc\\jemalloc_vc2017.sln /m /p:Configuration={} /p:PlatformToolset={}'.
                    format(self.settings.build_type, known_toolchains[str(self.settings.get_safe("compiler.version"))]))

        else:
            raise NotImplementedError('Platform not supported')

    def package(self):
        if self.settings.os == 'Linux':
            pass
        elif self.settings.os == 'Windows':
            self.copy(pattern='jemalloc.h',
                      src='include/jemalloc',
                      dst='include/jemalloc')
            self.copy(pattern='strings.h',
                      src='include/msvc_compat',
                      dst='include')
            self.copy(pattern='*.lib',
                      src='msvc/x64/{}'.format(self.settings.build_type),
                      dst='lib')
            self.copy(pattern='*.dll',
                      src='msvc/x64/{}'.format(self.settings.build_type),
                      dst='lib')
            self.copy(pattern='*.exe',
                      src='msvc/x64/{}'.format(self.settings.build_type),
                      dst='lib')
            self.copy(pattern='*.pdb',
                      src='msvc/x64/{}'.format(self.settings.build_type),
                      dst='lib')
        else:
            raise NotImplementedError('Platform not supported')

        self.copy(pattern='*', src='cmake', dst='cmake')

    def package_info(self):
        self.cpp_info.libs = ['jemalloc']
