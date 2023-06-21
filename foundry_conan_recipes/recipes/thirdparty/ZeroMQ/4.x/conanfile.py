# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os, shutil
import tempfile
from conans import ConanFile, tools, CMake, MSBuild

class ZeroMQConan(ConanFile):
    name = "ZeroMQ"
    license = "LGPL-3.0-or-later"
    author = "Pieter Hintjens"
    url = "https://github.com/zeromq/libzmq"
    description = """The ZeroMQ lightweight messaging kernel is a library which extends the standard socket interfaces 
                     with features traditionally provided by specialised messaging middleware products"""
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    exports_sources = "*"
    no_copy_source = True
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _get_library_name(self):
        static = "" if self.settings.os == "Windows" else "" if self.options.shared else "-static"
        return "libzmq{}".format(static)

    @property
    def _get_msbuild_configuration(self):
        dynamic = "Dyn" if self.options.shared else "Static"
        return "{}{}".format(dynamic, self.settings.build_type)

    def _get_msbuild_directory(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        builds_path = os.path.join(src_dir, "builds", "msvc")

        vs_dir_map = {"15": "vs2017"}
        vs_dir = vs_dir_map.get(str(self.settings.compiler.version))

        if None is vs_dir:
            raise RuntimeError("Compiler {} is currently unsupported".format(self.settings.compiler.version))

        return os.path.join(builds_path, vs_dir)

    def _use_ms_build(self):
        return (self.settings.os == "Windows"
                and not tools.Version(self.version) >= "4.3")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        # pkg-config is required since 4.3.3. Some platforms provide this
        # tool, but not all of them.
        # At this point, it is not known which version Conan is building, so
        # the requirement needs to be added regardless.
        if self.settings.os == "Macos":
            self.build_requires("pkgconfig/0.29.2@thirdparty/development")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

        if self._use_ms_build():
            self._upgrade_ms_build_scripts()
        elif self.settings.os == "Windows":
            self._fix_cmake_postfixes_in_msvc()

    def _upgrade_ms_build_scripts(self):
        # Need to retarget solution for latest SDK if using visual Studio 2017 (as a bug means this can't be done as part of upgrade)
        if self.settings.compiler.version == "15":
            old_sdk_version = "10.0.14393.0"
            new_sdk_version = "10.0.17763.0"

            project_file = os.path.join(self._get_msbuild_directory(), "libzmq", "libzmq.vcxproj")
            tools.replace_in_file(project_file, old_sdk_version, new_sdk_version, False)
        else:
            raise RuntimeError("Compiler {} is currently unsupported".format(self.settings.compiler))

    def _fix_cmake_postfixes_in_msvc(self):
        # In Windows, `.lib/pdb/dll` files get very descriptive names (e.g.
        # `libzmq-mt-gd-4_3_3.lib`). To avoid that, we get rid of the
        # postfixes.
        postfixes = (
            "${MSVC_TOOLSET}-mt-${ZMQ_VERSION_MAJOR}_${ZMQ_VERSION_MINOR}_${ZMQ_VERSION_PATCH}",
            "${MSVC_TOOLSET}-mt-gd-${ZMQ_VERSION_MAJOR}_${ZMQ_VERSION_MINOR}_${ZMQ_VERSION_PATCH}",
            "${MSVC_TOOLSET}-mt-s-${ZMQ_VERSION_MAJOR}_${ZMQ_VERSION_MINOR}_${ZMQ_VERSION_PATCH}",
            "${MSVC_TOOLSET}-mt-sgd-${ZMQ_VERSION_MAJOR}_${ZMQ_VERSION_MINOR}_${ZMQ_VERSION_PATCH}",
        )
        with tools.chdir(
                os.path.join(self.source_folder, self._source_subfolder)):
            for postfix in postfixes:
                tools.replace_in_file("CMakeLists.txt",
                                      postfix,
                                      "",
                                      strict=False)

    def _configure_cmake(self):
        cmake = CMake(self)

        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.settings.os == "Macos":
            cmake.definitions["ZMQ_BUILD_FRAMEWORK"] = "OFF"
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"

        cmake.definitions["BUILD_SHARED"] = self.options.shared
        cmake.definitions["BUILD_STATIC"] = not self.options.shared

        # Since 4.3.x, both shared and static libraries have "zmq" as basename
        # by default. `ZMQ_OUTPUT_BASENAME` can be set to override it. For
        # consistency with the 4.2.x line, the "-static" suffix will be
        # appended for static builds.
        if not self.options.shared and self.settings.os in ("Linux", "Macos"):
            cmake.definitions["ZMQ_OUTPUT_BASENAME"] = "zmq-static"

        # By default, perf-tools are not built in debug builds. For
        # completeness, enable them for all build types.
        cmake.definitions["WITH_PERF_TOOL"] = "ON"

        if self.settings.os in ("Linux", "Macos"):
            cmake.definitions["ENABLE_INTRINSICS"] = "ON"

        # Avoid installing runtime libraries (`msvcp140.dll`, etc.) in Windows.
        if self.settings.os == "Windows":
            cmake.definitions["ENABLE_CPACK"] = "OFF"

        # Specify where the pkg-config tool is located for those platforms
        # that use our internal build.
        if tools.Version(self.version) >= "4.3.3":
            if self.settings.os == "Macos":
                pkgconfig_path = os.path.join(
                    self.deps_cpp_info["pkgconfig"].bin_paths[0], "pkg-config")
                cmake.definitions["PKG_CONFIG_EXECUTABLE"] = pkgconfig_path

        # Newer versions of ZeroMQ will autogenerate a CMake config file
        # However, we already generate and provide our own `ZeroMQConfig.cmake`
        # file (see `ZeroMQConfig.cmake.in`), which uses `ZeroMQ::ZeroMQ` as
        # the target name, rather than the official `libzmq` and
        # `libzmq-static` names. To avoid a mix, the autogenerated files will
        # be sent directly to the trash.
        if tools.Version(self.version) >= "4.3":
            cmake.definitions["ZEROMQ_CMAKECONFIG_INSTALL_DIR"] = \
                tempfile.gettempdir()

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        if self._use_ms_build():
            msbuild_platforms = {"x86": "Win32", "x86_64": "x64"}
            msbuild = MSBuild(self)
            msbuild.build(
                os.path.join(self._get_msbuild_directory(), "libzmq.sln"),
                targets=["libzmq"],
                upgrade_project=False,
                platforms=msbuild_platforms,
                build_type=self._get_msbuild_configuration
            )
        else:
            cmake = self._configure_cmake()
            cmake.build()

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        is_linux = self.settings.os == "Linux"
        tokens = {}
        if self.options.shared:
            tokens["ZEROMQ_LIBTYPE"] = "SHARED"
            tokens["ZEROMQ_LIBEXT"] = ".dll" if is_windows else ".so" if is_linux else ".dylib"
            tokens["ZEROMQ_LIBDIR"] = "bin" if is_windows else "lib"
        else:
            tokens["ZEROMQ_LIBTYPE"] = "STATIC"
            tokens["ZEROMQ_LIBEXT"] = ".lib" if is_windows else ".a"
            tokens["ZEROMQ_LIBDIR"] = "lib"

        tokens["ZEROMQ_LIBNAME"] = self._get_library_name

        config_in_path = os.path.join(self.source_folder, "ZeroMQConfig.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(config_out_dir, "ZeroMQConfig.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def package(self):
        if self._use_ms_build():
            src_dir = os.path.join(self.source_folder, self._source_subfolder)
            bin_dir = os.path.join(src_dir, "bin")
            include_dir = os.path.join(src_dir, "include")
            self.copy("*.lib", "lib", "{}".format(bin_dir), keep_path=False)
            self.copy("*.dll", "bin", "{}".format(bin_dir), keep_path=False)
            self.copy("*.pdb", "bin", "{}".format(bin_dir), keep_path=False)
            self.copy("*.h", "include", "{}".format(include_dir), keep_path=True)
        else:
            cmake = self._configure_cmake()
            cmake.install()

            lib_path = os.path.join(self.package_folder, "lib")

            # remove pkgconfig folder
            pkgfolder = os.path.join(lib_path, "pkgconfig")
            if os.path.isdir(pkgfolder):
                shutil.rmtree(pkgfolder)

            # both static and dynamic libs are built, but we only want dynamic when building shared
            if self.options.shared:
                staticlib_path = os.path.join(lib_path, "libzmq-static.a")
                if os.path.isfile(staticlib_path):
                    os.unlink(staticlib_path)

        self._write_cmake_config_file()

    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = [self._get_library_name]

