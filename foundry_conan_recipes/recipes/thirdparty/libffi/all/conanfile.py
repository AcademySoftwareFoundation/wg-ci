# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, tools, AutoToolsBuildEnvironment
from jinja2 import Environment, FileSystemLoader
import os

class libffiConan(ConanFile):
    name = 'libffi'
    license = 'MIT'
    author = 'Anthony Green'
    url = 'https://github.com/libffi/libffi'
    description = 'A portable, high level programming interface to various calling conventions'
    homepage = 'https://sourceware.org/libffi/'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [False], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    revision_mode = 'scm'
    no_copy_source = False  # Builds in-source
    exports_sources = '*.cmake.in'

    package_originator = 'External'
    package_exportable = True

    @property
    def _source_subfolder(self):
        return 'libffi_src'

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'], branch='main')
        git.checkout(version_data['git_hash'])

        if self.settings.os == 'Windows':
            # Cygwin is required with at least the following packages:
            #    * autoconf
            #    * make
            # Since the VM may not feature Cygwin, an standalone archive will
            # be downloaded.
            git = tools.Git(folder='cygwin-standalone')
            git.clone(
                'git@a_gitlab_url:libraries/conan/thirdparty/cygwin-standalone.git',
                branch='foundry/v3.3.4',
                shallow=True)
            tools.untargz('cygwin-standalone/cygwin64.tgz')
            # There are issues with CLRF line endings, lets make sure these are
            # not a problem.
            # Raised issues like:
            # `error: AC_CONFIG_MACRO_DIRS([m4]) conflicts with ACLOCAL_AMFLAGS=-I m4`
            # or
            # `libffi/3.4.2@thirdparty/development: autoreconf: unrecognized option '-
            # '.`
            # Noticing the issues in endlines.  This didnt appear to be a problem on
            # local machines with older git versions, but manifested on the CI and
            # jenkins machines.
            # We have attempted to fix this by removing the .gitattribute on the libffi source
            # itself. However, this fixed the issue on Gitlab CI, but not Jenkins, where the similar
            # issues arose again, leading us to ensure during the conan steps that there are no
            # CLRF line endings.
            for rootdir, dirpaths, filepaths in os.walk(self._source_subfolder, topdown=True):
                for dirpath in list(dirpaths):
                    if dirpath.startswith('.git'):
                        dirpaths.remove(dirpath)
                for filepath in filepaths:
                    if filepath.startswith('.git'):
                        continue
                    tools.dos2unix(os.path.join(rootdir, filepath))

    def _get_autotools_args(self):
        """ Generates the args to be provided to the configure method."""
        args = []
        args.append('--enable-static=yes')
        args.append('--enable-shared=no')
        args.append('--disable-docs')

        if self.settings.build_type == 'Debug':
            args.append('--enable-debug')
        return args

    def build(self):
        libffi_src_dir = os.path.join(self.source_folder, self._source_subfolder).replace('\\', '/')
        args = self._get_autotools_args()

        with tools.chdir(libffi_src_dir):
            if self.settings.os == 'Windows':
                # Must replace with Linux path types, since we're running in shell mode.
                msvcc_sh_path = os.path.join(libffi_src_dir, 'msvcc.sh').replace('\\', '/')
                cygwin_bin_dir = os.path.join(self.source_folder, 'cygwin64', 'bin').replace('\\', '/')
                conf_env = {
                    'PATH': [cygwin_bin_dir],
                    'CC': f'{msvcc_sh_path} -m64',
                    'LD': 'link',
                    'CFLAGS': '-DFFI_BUILDING'}# Required to denote static building
                with tools.environment_append(conf_env):
                    self.run('sh autogen.sh')
                    self.run('sh configure {}'.format(' '.join(args)))
                    self.run('sh -c "make -j"')
            else:
                autotools = AutoToolsBuildEnvironment(self)
                self.run('sh autogen.sh {}'.format(' '.join(args)))
                autotools.configure(args=args, configure_dir=libffi_src_dir)
                autotools.make()

    def _write_cmake_config_file(self):
        p = os.path.join(self.package_folder, 'cmake')
        if not os.path.exists(p):
            os.mkdir(p)

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {'os': self.settings.os}
            interpreter_template = env.get_template(file_name + '.in')
            interpreter_template.stream(data).dump(os.path.join(self.package_folder, 'cmake', file_name))

        _configure('libffiConfig.cmake')

    def package(self):
        self.copy('LICENSE', src=self._source_subfolder, dst='licenses')
        if self.settings.os == 'Windows':
            build_folder = os.path.join(self.build_folder, self._source_subfolder, 'x86_64-pc-cygwin')
            self.copy('*.lib', src=os.path.join(build_folder, '.libs'), dst='lib')
            self.copy('*.h', src=os.path.join(build_folder, 'include'), dst='include')
        else:
            libffi_src_dir = os.path.join(self.build_folder, self._source_subfolder)
            autotools = AutoToolsBuildEnvironment(self)
            args = self._get_autotools_args()
            autotools.configure(args=args, configure_dir=libffi_src_dir)
            autotools.install()
        self._write_cmake_config_file()

    def package_info(self):
        self.cpp_info.libs = ["ffi"]
        if self.settings.os == "Linux":
            self.cpp_info.libdirs = ["lib64"]
