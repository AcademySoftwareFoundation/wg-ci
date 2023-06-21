# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class LuaConan(ConanFile):
    name = 'Lua'
    license = 'MIT'
    author = "Roberto Ierusalimschy, Waldemar Celes and Luiz Henrique de Figueiredo"
    url = 'https://github.com/lua/lua'
    description = 'Lua is a powerful, efficient, lightweight, embeddable ' \
                  'scripting language. It supports procedural programming, ' \
                  'object-oriented programming, functional programming, ' \
                  'data-driven programming, and data description.'

    settings = 'os', 'compiler', 'build_type', 'arch'

    options = {'shared': [True, False], 'fPIC': [True]}
    default_options = {'shared': False, 'fPIC': True}

    exports_sources = '*'
    no_copy_source = True

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git()
        git.clone(version_data['git_url'], 'master')
        git.checkout(version_data['git_hash'])

    def build(self):
        cmake = CMake(self)

        cmake.definitions['LUA_USE_CXX_EXCEPTIONS'] = '1'
        if self.options.shared:
            cmake.definitions['LUA_SHARED_ONLY'] = '1'
        else:
            cmake.definitions['LUA_STATIC_ONLY'] = '1'
        cmake.definitions['LUA_VERSION'] = self.version

        cmake.configure(source_folder=self.source_folder)
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ['lua']
