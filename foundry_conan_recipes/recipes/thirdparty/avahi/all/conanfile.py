# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class Avahi(ConanFile):
    name = 'avahi'
    description = 'Avahi service discovery suite.'
    url = 'http://avahi.org/'
    license = 'LGPL-2.1-only'
    author = 'Lennart Poettering and Trent Lloyd'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True]}
    default_options = {'shared': True}

    exports_sources = 'cmake/*.cmake'
    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    build_requires = 'Qt/[~5.15]'

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        autotools = self._configure()
        autotools.make()

    def package(self):
        self.copy('AvahiConfig.cmake', 'cmake', 'cmake')

        excludes = [
            'avahi-autoipd',
            'avahi-compat-howl',
            'avahi-daemon',
            'avahi-glib',
            'avahi-gobject',
            'avahi-libevent',
            'avahi-ui',
            'avahi-utils'
        ]

        self.copy('*.h', dst='include', src=self._source_subfolder, excludes=excludes)

        self.copy('*.so*', dst='lib', src='.', keep_path=False)

    def _configure(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        with tools.environment_append(self._environment):        
            with tools.chdir(src_dir):
                self.run('./autogen.sh')

            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(configure_dir=self._source_subfolder, args=self._configure_args)
            return autotools

    @property
    def _configure_args(self):
        yes_no = lambda v: 'yes' if v else 'no'

        args = [
            '--enable-shared={}'.format(yes_no(self.options.shared)),
            '--enable-static={}'.format(yes_no(not self.options.shared)),
            '--disable-gdbm',
            '--disable-glib',
            '--disable-gobject',
            '--disable-gtk',
            '--disable-gtk3',
            '--disable-libdaemon',
            '--disable-libevent',
            '--disable-manpages',
            '--disable-mono',
            '--disable-python',
            '--disable-qt4',
            '--enable-qt5',
            '--disable-xmltoman',
            '--enable-compat-libdns_sd'
        ]

        return args

    @property
    def _environment(self):
        env = {'NOCONFIGURE': '1'}

        qt_bin = self.deps_cpp_info['Qt'].bin_paths[0]
        qt_inc = self.deps_cpp_info['Qt'].include_paths[0]
        qt_lib = self.deps_cpp_info['Qt'].lib_paths[0]

        env['MOC_QT5'] = os.path.join(qt_bin, 'moc')
        env['QT5_CFLAGS'] = f"-DQT_CORE_LIB -I{os.path.join(qt_inc, 'QtCore')} -I{qt_inc} -fPIC"
        env['QT5_LIBS'] = f'-L{qt_lib} -lQt5Core'

        return env

    @property
    def _source_subfolder(self):
        return '{}_src'.format(self.name)
