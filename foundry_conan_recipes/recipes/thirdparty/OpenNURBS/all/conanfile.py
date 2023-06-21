# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, MSBuild, tools
from jinja2 import Environment, FileSystemLoader

class OpenNURBSConan(ConanFile):
    name = "opennurbs"
    settings = "os", "compiler", "build_type", "arch"
    description = "The openNURBS Initiative provides CAD, CAM, CAE, and " \
                   "computer graphics software developers the"            \
                   "tools to accurately transfer 3D geometry between"     \
                   "applications."
    url = "https://www.rhino3d.com/opennurbs/"
    license = "OpenNURBS"
    author = "Robert McNeel & Associates"
    
    options = { "shared": [False], "fPIC": [True, False] }
    default_options = { "shared": False, "fPIC": True }

    exports_sources = '*.cmake.in'

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    @property
    def _library_name(self):
        if self.settings.os == "Windows":
            return "opennurbs_public_staticlib"
        else:
            return "opennurbs_public"

    @property
    def _source_subfolder(self):
        return '{}_src'.format(self.name)

    def source(self):
        version_data = self.conan_data['sources'][self.version]

        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        if self.settings.os == "Windows":
            msbuild = MSBuild(self)
            targets = [self._library_name]
            sln_path = os.path.join(self.build_folder, self._source_subfolder, "opennurbs_public.sln")
            msbuild.build(sln_path, targets=targets, upgrade_project=False)
        else:
            args = 'EXTRA_FLAGS=-fPIC' if self.options.fPIC else ''
            self.run(f"make {args} all", cwd=os.path.join(self.build_folder, self._source_subfolder))

    def _write_cmake_config_file(self):
        p = os.path.join(self.package_folder, "cmake")
        if not os.path.exists(p):
            os.mkdir(p)

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {
                "os": self.settings.os
            }

            data["LIBRARY_NAME"] = self._library_name

            is_windows = self.settings.os == "Windows"
            data["LIBRARY_PREFIX"] = "" if is_windows else "lib"
            data["LIBRARY_SUFFIX"] = ".lib" if is_windows else ".a"
           
            interpreter_template = env.get_template(file_name + ".in")
            p = os.path.join(self.package_folder, "cmake", file_name)
            interpreter_template.stream(data).dump(p)
        
        _configure("OpenNURBSConfig.cmake")

    def package(self):
        self.copy("opennurbs*.h", "./include",
                  src=os.path.join(self.build_folder, self._source_subfolder),
                  keep_path=True)

        if self.settings.os == "Windows":
            path = "{}/bin/x64/{}".format(os.path.join(self.build_folder, self._source_subfolder),
                                          self.settings.build_type)

            self.copy("{}.lib".format(self._library_name), "lib", path, keep_path=False)
            self.copy("{}.pdb".format(self._library_name), "lib", path, keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)

        self._write_cmake_config_file()

    def package_info(self):
        self.cpp_info.libs = [self._library_name]
