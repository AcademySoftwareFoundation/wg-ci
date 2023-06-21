# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, tools


class LuaJITConan(ConanFile):
    name = 'LuaJIT'
    license = 'MIT'
    author = "Michael Pall"
    url = 'https://github.com/LuaJIT/LuaJIT'
    description = 'LuaJIT is a Just-In-Time (JIT) compiler for the Lua ' \
                  'programming language.'

    settings = 'os', 'compiler', 'build_type', 'arch'

    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    exports_sources = '*'

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    @property
    def lua_abi_version_major(self):
        return '5'

    @property
    def lua_abi_version_minor(self):
        return '1'

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git()
        git.clone(version_data['git_url'], 'master')
        git.checkout(version_data['git_hash'])

    def build(self):
        if self.settings.os in ('Linux', 'Macos'):
            # Compile and install.
            with tools.chdir(self.source_folder):
                o_level = 0 if self.settings.build_type == 'Debug' else 2
                command_args = [
                    'make',
                    'amalg',
                    '-j',
                    # On x64, LuaJIT has historically used 32-bit addresses.
                    # While this has changed in recent versions (see
                    # https://github.com/LuaJIT/LuaJIT/commit/bd00094c3b50e193fb32aad79b7ea8ea6b78ed25),
                    # the flag to enable 64-bit addresses will still be passed.
                    'XCFLAGS=-DLUAJIT_ENABLE_GC64',
                    'CCDEBUG=-g',
                    'CCOPT=" -O{} -fomit-frame-pointer"'.format(o_level),
                ]
                if self.options.shared or self.options.fPIC:
                    command_args.append('CFLAGS=-fPIC')
                command = ' '.join(command_args)
                self.run(command)

                command_args = [
                    'make',
                    'install',
                    'PREFIX="{}"'.format(self.package_folder),
                ]
                command = ' '.join(command_args)
                self.run(command)

            # Fix install name in macOS.
            if self.options.shared and self.settings.os == 'Macos':
                version = self.version.split('-')[0]
                version_major, version_minor, version_patch = \
                    version.split('.')
                dylib_name = 'libluajit-{}.{}.{}.{}.{}.dylib'.format(
                    self.lua_abi_version_major, self.lua_abi_version_minor,
                    version_major, version_minor, version_patch)
                dylib_path = os.path.join(self.package_folder, 'lib',
                                          dylib_name)
                self.run('install_name_tool -id @rpath/{} {}'.format(
                    dylib_name, dylib_path))

            # Strip libraries that are not going to be used
            if self.options.shared:
                extension_to_strip = 'a'
            elif self.settings.os == 'Linux':
                extension_to_strip = 'so'
            else:
                extension_to_strip = 'dylib'
            self.run('rm -f {0}/lib/*.{1} {0}/lib/*.{1}.*'.format(
                self.package_folder, extension_to_strip))

            # Create symlink to `luajit` executable.
            bin_dir = '{}/bin'.format(self.package_folder)
            files_in_bin_dir = os.listdir(bin_dir)
            for file_name in files_in_bin_dir:
                if file_name.startswith('luajit-'):
                    executable_name = file_name
                    self.run('ln -sf {} {}/luajit'.format(
                        executable_name, bin_dir))
                    break
            else:
                raise RuntimeError(
                    'Unabled to create symlink to "luajit" executable.')

        elif self.settings.os == 'Windows':
            with tools.chdir(self.source_folder + '/src'):
                # Note that `msvcbuild.bat` is really fragile, and breaks if
                # the given parameters are not in the expected order:
                #
                #   1. [nogc64] o [gc64] (depends on version)
                #   2. [debug]
                #   3. [amalg|static]

                script_path = \
                    '{}/src/msvcbuild.bat'.format(self.source_folder)
                command_args = ['"{}"'.format(script_path)]

                # Historically, the GC64 support was disabled by default, with
                # an opt-in parameter (`gc64`) to switch it on. However, that
                # has changed recently; now an opt-out option (`nogc64`) is
                # provided (see
                # https://github.com/LuaJIT/LuaJIT/commit/bd00094c3b50e193fb32aad79b7ea8ea6b78ed25).
                # In order to support previous versions of LuaJIT, we need to
                # check whether the `nogc64` option is present in the script,
                # in which case there is no need to pass `gc64`, as it's
                # enabled by default.
                with open(script_path, 'r') as f:
                    if 'nogc64' not in f.read():
                        command_args.append('gc64')

                # The "debug" option is misleading, as it only enables or
                # disables debug symbols generation.
                command_args.append('debug')

                if self.options.shared:
                    command_args.append('amalg')
                else:
                    command_args.append('static')

                command = ' '.join(command_args)

                # The `msvcbuild.bat` script is hardcoded to generate optimized
                # builds; certain flags need to be swapped on the flay before
                # running the build script.
                replacements = {}
                replacements['/O2 '] = '/O0 '
                replacements['/MD '] = '/MDd '
                for old, new in replacements.items():
                    if self.settings.build_type == 'Release':
                        old, new = new, old
                    tools.replace_in_file(script_path, old, new, strict=False)

                if self.options.shared:
                    self.run(command)
                else:
                    # For static libraries, the PDB file we want is produced by
                    # the compiler, not the linker; we need to explicitly name
                    # it, or else it's called "VC100.pdb", or "VC140.pdb", ...
                    lua_abi_version = '{}{}'.format(self.lua_abi_version_major,
                                                    self.lua_abi_version_minor)
                    cl = os.environ.get('CL', '')
                    cl = '{} -Fdlua{}_static'.format(lua_abi_version,
                                                     cl).strip()
                    with tools.environment_append({'CL': cl}):
                        self.run(command)
                    os.rename('lua{}.lib'.format(lua_abi_version),
                              'lua{}_static.lib'.format(lua_abi_version))

        else:
            raise ValueError('Unsupported platform {}'.format(
                self.settings.os))

    def package(self):
        self.copy('*', dst='cmake/', src='cmake/', symlinks=True)

        version = self.version.split('-')[0]
        version_major, version_minor, version_patch = version.split('.')

        cmake_template_file_path = os.path.join(self.package_folder, 'cmake',
                                                'LuaJITConfig.cmake.in')
        cmake_file_path = cmake_template_file_path[:-3]
        file_content = open(cmake_template_file_path, 'r').read()
        os.remove(cmake_template_file_path)
        wildcard_dict = {}
        wildcard_dict['@@LUA_ABI_VERSION_MAJOR@@'] = self.lua_abi_version_major
        wildcard_dict['@@LUA_ABI_VERSION_MINOR@@'] = self.lua_abi_version_minor
        wildcard_dict['@@VERSION_MAJOR@@'] = version_major
        wildcard_dict['@@VERSION_MINOR@@'] = version_minor
        wildcard_dict['@@VERSION_PATCH@@'] = version_patch
        wildcard_dict['@@APPLE_SUFFIX@@'] = \
            '.dylib' if self.options.shared else '.a'
        wildcard_dict['@@UNIX_SUFFIX@@'] = \
            '.so' if self.options.shared else '.a'
        wildcard_dict['@@WIN32_SUFFIX@@'] = \
            '.lib' if self.options.shared else '_static.lib'
        for wildcard, value in wildcard_dict.items():
            file_content = file_content.replace(wildcard, value)
        with open(cmake_file_path, 'w') as text_file:
            text_file.write(file_content)

        cmake_version_template_file_path = os.path.join(
            self.package_folder, 'cmake', 'LuaJITConfigVersion.cmake.in')
        cmake_version_file_path = cmake_version_template_file_path[:-3]
        file_content = open(cmake_version_template_file_path, 'r').read()
        os.remove(cmake_version_template_file_path)
        file_content = file_content.replace('@@VERSION@@', version)
        with open(cmake_version_file_path, 'w') as text_file:
            text_file.write(file_content)

        if self.settings.os == 'Windows':
            include_dst = 'include/luajit-{}.{}'.format(
                version_major, version_minor)
            self.copy('lauxlib.h', src='src', dst=include_dst)
            self.copy('luaconf.h', src='src', dst=include_dst)
            self.copy('lua.h', src='src', dst=include_dst)
            self.copy('lua.hpp', src='src', dst=include_dst)
            self.copy('luajit.h', src='src', dst=include_dst)
            self.copy('lualib.h', src='src', dst=include_dst)
            self.copy('lua51.lib', src='src', dst='lib')
            self.copy('lua51.dll', src='src', dst='bin')
            self.copy('lua51.pdb', src='src', dst='bin')
            self.copy('lua51_static.lib', src='src', dst='lib')
            self.copy('lua51_static.pdb', src='src', dst='bin')
            self.copy('luajit.exe', src='src', dst='bin')
            self.copy('luajit.pdb', src='src', dst='bin')
            self.copy('jit', src='src', dst='bin')
            self.copy('*.lua', src='src/jit', dst='bin/lua/jit')
            self.copy('*', src='dot', dst='dot')

    def package_info(self):
        self.cpp_info.libs = ['luajit']
