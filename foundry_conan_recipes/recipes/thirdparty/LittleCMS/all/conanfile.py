# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, MSBuild, tools, AutoToolsBuildEnvironment
from jinja2 import Environment, FileSystemLoader

class LittleCMS(ConanFile):
    name = "LittleCMS"
    author = "Marti Maria"
    settings = "os", "arch", "compiler", "build_type"
    description = "A free, open source, CMM engine."
    url = "https://www.littlecms.com/"
    license = "MIT"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = { "shared": False, "fPIC": True }

    exports_sources = "*cmake.in"

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _library_name(self):
        if self.settings.os == "Windows":
            return "lcms2" if self.options.shared else "lcms2_static"
        else:
            return "liblcms2"

    @property
    def _run_unit_tests(self):
        return "LittleCMS_RUN_UNITTESTS" in os.environ

    @property
    def _msvs_year(self):
        msvs_years = {
            "15": "2017",
            "16": "2019",
            "17": "2019",
        }
        return msvs_years[str(self.settings.compiler.version)]

    @property
    def _msvs_project_folder(self):
        return os.path.join(self.source_folder, self._source_subfolder, "Projects", f"VC{self._msvs_year}")

    @property
    def _msvs_target(self):
        return "lcms2_DLL" if self.options.shared else "lcms2_static"

    def _upgrade_ms_build_scripts(self):
        # Need to retarget solution for latest SDK if using visual Studio 2017
        if self.settings.compiler.version == "15":
            old_sdk_version = "10.0.17134.0"
            new_sdk_version = "10.0.19041.0"

            target = self._msvs_target
            project_file = os.path.join(self._msvs_project_folder, target, f"{target}.vcxproj")
            tools.replace_in_file(project_file, old_sdk_version, new_sdk_version, False)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        version_data = self.conan_data["sources"][self.version]

        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

        if self.settings.os == "Windows":
            self._upgrade_ms_build_scripts()

    def build(self):
        if self.settings.os == "Windows":
            msbuild  = MSBuild(self)
            sln_path = os.path.join(self._msvs_project_folder, "lcms2.sln")
            msbuild.build(sln_path, targets=[self._msvs_target], upgrade_project=False)
        else:
            autotools = AutoToolsBuildEnvironment(self)
            autotools_vars = autotools.vars

            config_args = []
            if self.settings.build_type == "Debug":
                autotools_vars["CFLAGS"] += " -g -O0"

            if not self.options.shared:
                autotools_vars["CFLAGS"] += " -fvisibility=hidden"
                config_args.append("--disable-shared")
            else:
                config_args.append("--disable-static")

            with tools.environment_append(autotools_vars):
                src_dir = os.path.join(self.source_folder, self._source_subfolder)
                autotools.configure(configure_dir=src_dir, args=config_args)
                autotools.make()
                if self._run_unit_tests:
                    autotools.make(target="check")
                autotools.install(args=["-j1"])

    def _write_cmake_config_file(self):
        p = os.path.join(self.package_folder, "cmake")
        if not os.path.exists(p):
            os.mkdir(p)

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            versionTokens = self.version.split(".")
            data = {
                "version_major": str(versionTokens[0]),
                "version_minor": str(versionTokens[1]),
                "os": self.settings.os,
                "shared": self.options.shared,
            }

            data["LIBRARY_NAME"] = self._library_name

            data["libsuffix"] = ".a"
            if self.options.shared:
                data["libsuffix"] = ".dylib" if self.settings.os == "Macos" else ".so"

            interpreter_template = env.get_template(file_name + ".in")
            interpreter_template.stream(data).dump(os.path.join(self.package_folder, "cmake", file_name))

        _configure("LittleCMSConfig.cmake")
        _configure("LittleCMSConfigVersion.cmake")

    def package(self):
        if self.settings.os == "Windows":
            src_dir = os.path.join(self.source_folder, self._source_subfolder)
            self.copy("include/*.h", ".", src=src_dir, keep_path=True)

            if self.options.shared:
                self.copy("{}.lib".format(self._library_name), "lib", "{}/bin".format(src_dir), keep_path=False)
                self.copy("{}.dll".format(self._library_name), "bin", "{}/bin".format(src_dir), keep_path=False)
                self.copy("{}.pdb".format(self._library_name), "bin", "{}/bin".format(src_dir), keep_path=False)
            else:
                self.copy("{}.lib".format(self._library_name), "lib", "{}/Lib/MS".format(src_dir), keep_path=False)

                pdb_dir = os.path.join(self._msvs_project_folder, self._msvs_target, "Release_x64")
                self.copy("{}.pdb".format(self._library_name), "bin", pdb_dir, keep_path=False)

        elif self.settings.os == "Macos" and self.options.shared:
            versionTokens = self.version.split(".")
            lib_path = os.path.join(self.package_folder, "lib")
            # Make the dylib's relocatable
            dylib_path = os.path.join(lib_path, "{}.{}.dylib".format(self._library_name, versionTokens[0]))
            args = ["install_name_tool", "-id", "@rpath/{}.dylib".format(self._library_name), dylib_path]
            self.run(" ".join(args))

        self._write_cmake_config_file()

    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = [self._library_name]

