# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools


class ZipstreamConan(ConanFile):
    name = "Zipstream"
    description = "Streaming wrapper around zlib"
    license = "zlib-acknowledgement" # zlib/libpng stated in headers themselves
    author = "Jonathan de Halleux"
    url = "https://www.codeproject.com/articles/4457/zipstream-bzip2stream-iostream-wrappers-for-the-zl"
    revision_mode = "scm"

    exports_sources = ["*.cmake"]
    no_copy_source = False

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'

    # Although zipstream is header only, it does require zlib.h.
    def requirements(self):
        self.requires("zlib/[~1.2.11]@thirdparty/development")

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def package(self):
        self.copy(pattern="*", src=os.path.join(self._source_subfolder, "include"), dst="include")
        self.copy(pattern="ZipstreamConfig.cmake", src="", dst="cmake" )

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
