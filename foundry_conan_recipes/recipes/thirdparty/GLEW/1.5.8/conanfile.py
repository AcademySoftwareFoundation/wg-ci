# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, MSBuild

class GlewConan(ConanFile):
    name = "GLEW"
    license = "MIT"
    author = "Nigel Stewart"
    url = "http://glew.sourceforge.net/"
    description = """The OpenGL Extension Wrangler Library (GLEW) is a cross-platform open-source C/C++ extension loading library, 
                     which provides efficient run-time mechanisms for determining which OpenGL extensions The OpenGL Extension Wrangler 
                     Library (GLEW) is a cross-platform open-source C/C++ extension loading library. GLEW provides efficient run-time 
                     mechanisms for determining which OpenGL extensions"""
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    exports_sources = "*"
    no_copy_source = False # source tree is mutated from release archives
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _library_name(self):
        if self.settings.os == "Windows":
            if self.options.shared:
                glew_libname = "glew32d" if self.settings.build_type == "Debug" else "glew32"
            else:
                glew_libname = "glew32sd" if self.settings.build_type == "Debug" else "glew32s"
        else:
            glew_libname = "libGLEW"
        return glew_libname

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

        if self.settings.os == "Windows":
            self._upgrade_ms_build_scripts(self._source_subfolder)
        else:
            # the config/config.guess file needs to be executable (it only has rw when cloned from git).
            # Without doing so the build will fail as the makefile uses this to check that the system is supported
            self.run("chmod u+x {}".format(os.path.join(self._source_subfolder, "config", "config.guess")))

    def _upgrade_ms_build_scripts(self, src_dir):
        msbuild = MSBuild(self)
        try:
            msbuild.build(os.path.join(src_dir, "build", "vc6", "glew.dsw"), targets=None, upgrade_project=True)
        except Exception as e:
            self.output.warn("There was an upgrade exception, but continuing:\n{}".format(e))

        replacements = {"x86": "x64", "Win32": "x64"}

        # Need to retarget solution for latest SDK if using visual Studio 2017 (as a bug means this isn't done as part of upgrade)
        if self.settings.compiler.version == "15":
            sdk_version = "10.0.17763.0"
            replacements["<PropertyGroup Label=\"Globals\">"] = "<PropertyGroup Label=\"Globals\"><WindowsTargetPlatformVersion>{}</WindowsTargetPlatformVersion>".format(sdk_version)

        project_files = ["glew.sln",
                         "glew_shared.vcxproj",
                         "glew_static.vcxproj",
                         "glewinfo.vcxproj",
                         "visualinfo.vcxproj"]

        for project in project_files:
            for old in replacements:
                tools.replace_in_file(os.path.join(src_dir, "build", "vc6", project), old, replacements[old], False)

        # there remains MSBUILD warnings regarding mismatching names, but they can be ignored

    def build(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        if self.settings.os == "Windows":
            msbuild = MSBuild(self)
            targets = ["glew_shared"] if self.options.shared else ["glew_static"]
            targets.extend(["glewinfo", "visualinfo"])
            sln_path = os.path.join(src_dir, "build", "vc6", "glew.sln")
            msbuild.build(sln_path, targets=targets, upgrade_project=False)
        else:
            target = "all" if self.settings.build_type == "Release" else "debug"
            self.run("make {}".format(target), cwd=src_dir)

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        is_linux = self.settings.os == "Linux"
        tokens = {}
        if self.options.shared:
            tokens["GLEW_LIBTYPE"] = "SHARED"
            tokens["GLEW_LIBEXT"] = ".dll" if is_windows else ".so" if is_linux else ".dylib"
        else:
            tokens["GLEW_LIBTYPE"] = "STATIC"
            tokens["GLEW_LIBEXT"] = ".lib" if is_windows else ".a"

        tokens["GLEW_LIBNAME"] = self._library_name

        config_in_path = os.path.join(self.source_folder, "GLEWConfig.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(config_out_dir, "GLEWConfig.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def package(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)

        self.copy("include/*", ".", src=src_dir, keep_path=True)

        if self.settings.os == "Windows":
            pdb_lib_flavour = "glew_shared" if self.options.shared else "glew_static"
            self.copy("{}.lib".format(self._library_name), "lib", "{}/lib".format(src_dir), keep_path=False)
            self.copy("{}.dll".format(self._library_name), "bin", "{}/bin".format(src_dir), keep_path=False)
            self.copy("*.exe", "bin", "{}/bin".format(src_dir), keep_path=False)
            self.copy("{}.pdb".format(pdb_lib_flavour), "bin" if self.options.shared else "lib", "{}/lib".format(src_dir), keep_path=False)
            self.copy("*.pdb", "bin", "{}/bin".format(src_dir), keep_path=False)
        else:
            if not self.options.shared:
                self.copy(pattern="*.a", dst="lib", keep_path=False)
            else:
                lib_extensions = ["*.dylib"] if self.settings.os == "Macos" else ["*.so", "*.so.*"]
                for extension in lib_extensions:
                    self.copy(pattern=extension, dst="lib", keep_path=False, symlinks=True)

                if self.settings.os == "Macos":
                    lib_path = os.path.join(self.package_folder, "lib")
                    # Make the dylib's relocatable
                    dylib_path = os.path.join(lib_path, "{}.{}.dylib".format(self._library_name, self.version))
                    args = ["install_name_tool", "-id", "@rpath/{}.dylib".format(self._library_name), dylib_path]
                    self.run(" ".join(args))

        self._write_cmake_config_file()

    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = ["GLEW"]

        if not self.options.shared:
            self.cpp_info.defines = ["GLEW_STATIC"]

