# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, tools


class PyZMQTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def build(self):
        pass

    def test(self):
        python_bin_path = os.path.join(
            self.deps_cpp_info["Python"].rootpath,
            self.deps_user_info["Python"].interpreter)
        python_version = tools.Version(self.deps_cpp_info["Python"].version)

        pyzmq_dir = self.deps_cpp_info["PyZMQ"].rootpath

        additional_env = {}
        additional_env['PYTHONHOME'] = os.path.join(
            self.deps_cpp_info["Python"].rootpath,
            self.deps_user_info["Python"].pyhome)
        additional_env['PYTHONPATH'] = pyzmq_dir
        additional_env['PYTHONDONTWRITEBYTECODE'] = '1'
        additional_env['PYTHONNOUSERSITE'] = '1'

        # Since Python 3.8, `PATH` is no longer used for searching dependent DLLs. PyZMQ cannot find
        # its `libzmq.dll` dependency unless the directory is added via `os.add_dll_directory()`.
        # See https://bugs.python.org/issue43173 (Not a bug really; behavior intentionally
        # introduced in Python 3.8.)
        if self.settings.os == 'Windows' and python_version >= '3.8.0':
            zmq_dir = os.path.join(self.deps_cpp_info["ZeroMQ"].rootpath, 'bin')
            additional_env['FN_PYTHON_DLL_DIRECTORIES'] = zmq_dir

        with tools.chdir(self.recipe_folder):
            with tools.environment_append(additional_env):
                self.run(python_bin_path + ' server_client_example.py',
                         run_environment=True)
