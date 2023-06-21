# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil

from conans import ConanFile, tools


class PyZMQConan(ConanFile):
    name = 'PyZMQ'
    license = 'BSD-3-Clause'
    author = 'Brian E. Granger'
    url = 'https://github.com/zeromq/pyzmq'
    description = 'PyZMQ: Python bindings for zeromq'

    settings = 'os', 'compiler', 'build_type', 'arch'

    options = {
        'python_version': [
            "2",
            "3",
            "3.9",
            "3.10",
        ],
    }
    default_options = {
        'python_version': "3",
    }

    exports_sources = 'setup.cfg'

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    requires = (('ZeroMQ/4.3.3@thirdparty/development'), )

    def requirements(self):
        if self.options.python_version == "2":
            self.requires('Python/2.7.18@thirdparty/development')
        elif self.options.python_version == "3":
            self.requires('Python/3.7.7@thirdparty/development')
        elif self.options.python_version == "3.9":
            self.requires('Python/3.9.10')
        else:
            self.requires('Python/3.10.10')

    @property
    def _source_subfolder(self):
        return '{}_src'.format(self.name)

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

        shutil.copy('setup.cfg', self._source_subfolder)

        if self.settings.os == 'Windows':
            if self.options.python_version == "2":
                with tools.chdir(self._source_subfolder):
                    os.remove('buildutils/include_win32/stdint.h')

            # After https://github.com/zeromq/libzmq/issues/110 was merged for
            # ZeroMQ 4.3.3, `SOCKET` is no longer defined in Windows.
            # `winsock2.h` needs to be included manually.
            #
            # Issue in the PyZMQ project:
            # https://github.com/zeromq/pyzmq/issues/1394
            #
            # Since the issue might be fixed by the time we upgrade to a newer
            # version (20.0.0+), only applying the temporary fix up to 19.0.2.
            if (tools.Version(self.deps_cpp_info['ZeroMQ'].version) >= '4.3.3'
                    and tools.Version(self.version) <= '19.0.2'):
                tools.replace_in_file(
                    os.path.join(self._source_subfolder,
                                 'zmq/backend/cython/libzmq.pxd'),
                    'cdef extern from "zmq_compat.h":',
                    'cdef extern from "winsock2.h":\n    pass\n\n'
                    'cdef extern from "zmq_compat.h":')

    def build(self):
        python_bin_path = os.path.join(
            self.deps_cpp_info["Python"].rootpath,
            self.deps_user_info["Python"].interpreter)
        python_lib_dir = self.deps_cpp_info['Python'].lib_paths[0]
        python_inc_dir = self.deps_cpp_info['Python'].include_paths[0]
        zeromq_root_path = self.deps_cpp_info['ZeroMQ'].rootpath

        additional_env = {}
        additional_env['PYTHONHOME'] = os.path.join(
            self.deps_cpp_info["Python"].rootpath,
            self.deps_user_info["Python"].pyhome)
        additional_env['PYTHONPATH'] = None
        additional_env['PYTHONNOUSERSITE'] = '1'

        is_windows = self.settings.os == 'Windows'
        is_release = self.settings.build_type == 'Release'
        is_python2 = self.options.python_version == "2"

        # Cython is required to build the PyZMQ extension. It will be installed
        # in the build folder using the `pip` module.
        # CA: The Cython package in Windows seems to fail to dynamically link
        # some libraries when using Python 2 Release; I believe this might be
        # an issue with the PyPI package itself, or with our Python 2 build.
        # `--no-cython-compile` will be used to compile Cython, rather than
        # using the CPython platform version from PyPI.
        no_cython_compile = is_windows and is_release and is_python2
        cython_install_dir = os.path.join(self.build_folder, 'CythonInstallDir')
        with tools.environment_append(additional_env):
            self.run(python_bin_path + ' -m pip install Cython==0.29.21' +
                     (' --install-option="--no-cython-compile"' if no_cython_compile else '') +
                     ' --no-warn-script-location --no-cache-dir --disable-pip-version-check' +
                     ' --target "{}"'.format(cython_install_dir))

        additional_env['PYTHONPATH'] = cython_install_dir

        build_args = ['build_ext' ,'--verbose']

        if not is_release:
            build_args.append('--debug')

        build_args.append('--zmq={}'.format(zeromq_root_path))
        build_args.append('--library-dirs={}'.format(python_lib_dir))
        build_args.append('--include-dirs={}'.format(python_inc_dir))

        if is_windows:
            build_args.append('--libzmq=libzmq')

            python_version = tools.Version(
                self.deps_cpp_info["Python"].version)
            python_lib_version_str = '{}{}'.format(python_version.major,
                                                   python_version.minor)
            python_lib_suffix = ''
            if not is_release:
                python_lib_suffix = '_d'
            build_args.append('--libraries=python{}{}'.format(
                python_lib_version_str, python_lib_suffix))

            # Distutils will try to find Visual Studio itself, and probably
            # fail.
            # See: https://docs.python.org/2.7/distutils/apiref.html#module-distutils.msvccompiler
            additional_env.update({'DISTUTILS_USE_SDK': '1', 'MSSdk': '1'})

            if is_release:
                additional_env.update({
                    '_CL_': '/Zi',
                    '_LINK_': '/DEBUG /OPT:REF',
                })

        if self.options.python_version == '3.10':
            build_command = [python_bin_path, '-m', 'pip',  'install', '.']
            global_option_build_args = []
            for arg in build_args:
                global_option_build_args.append('--global-option')
                global_option_build_args.append(arg)
            build_command.extend(global_option_build_args)
            build_command.append('--target={}'.format(
                self.package_folder))
        else:
            build_command = [python_bin_path, 'setup.py']
            build_command.extend(build_args)
            build_command.extend(['install', '--install-lib={}'.format(
                self.package_folder)])

        source_folder = os.path.join(self.source_folder,
                                     self._source_subfolder)
        with tools.chdir(source_folder):
            with tools.environment_append(additional_env):
                self.run(' '.join(build_command), run_environment=True)

    def package(self):
        pass
