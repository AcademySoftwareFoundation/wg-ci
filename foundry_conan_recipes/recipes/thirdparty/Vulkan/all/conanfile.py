# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

from jinja2 import Environment, FileSystemLoader

class VulkanConan(ConanFile):
    name = "Vulkan"
    settings = "os", "arch"
    description = "Vulkan SDK"
    url = "https://vulkan.lunarg.com/sdk/home"
    license = "VulkanSDK"
    author = "LunarG"
    revision_mode = "scm"

    exports_sources = "*.cmake.in"
    no_copy_source = True

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    def configure(self):
        if not self.settings.os in ["Windows", "Linux", "Macos"]:
            raise ConanInvalidConfiguration("Unsupported operating system!")

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'], args="-c core.longpaths=true")
        git.checkout(version_data['git_hash'])

    def build(self):
        self.output.info("Nothing to build, progress to packaging...")

    def _produce_config_files(self):
        os.makedirs(os.path.join(self.package_folder, "cmake"), exist_ok=True)

        v = self.version.split(".")
        data = {
            "version_major":    v[0],
            "version_minor":    v[1],
            "version_patch":    v[2],
            "version_bugfix":   v[3],
            "os": self.settings.os
        }

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _config_file(file_name):
            template = env.get_template(f"{file_name}.in")
            template.stream(data).dump(os.path.join(self.package_folder, "cmake", file_name))

        _config_file("VulkanConfig.cmake")
        _config_file("VulkanConfigVersion.cmake")
        _config_file("Vulkan_Targets.cmake")

    def package(self):
        self._produce_config_files()

        if self.settings.os == "Linux":
            src_path = os.path.join(self.source_folder, self._source_subfolder, "bin", "linux-64")
            self.copy(pattern="x86_64/*", src=src_path, keep_path=True, symlinks=True)

        elif self.settings.os == "Macos":
            src_path = os.path.join(self.source_folder, self._source_subfolder, "bin", "mac-64")
            self.copy(pattern="macOS/*", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern="MoltenVK/*", src=src_path, keep_path=True, symlinks=True)

        elif self.settings.os == "Windows":
            src_path = os.path.join(self.source_folder, self._source_subfolder, "bin", "win-64")
            self.copy(pattern="Bin/*.exe", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern="Bin/*.dll", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern="Lib/*.lib", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern="Config/*",  src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern="Include/*", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern="Runtime/x64/*.dll", src=src_path, keep_path=True, symlinks=True)

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.includedirs = ["x86_64/include"]
            self.cpp_info.libdirs = ["x86_64/lib"]
        elif self.settings.os == "Macos":
            self.cpp_info.includedirs = ["MoltenVK/include"]
            self.cpp_info.libdirs = ["macOS/lib", "MoltenVK/dylib/macOS"]
        #else default include/ and lib/

        self.cpp_info.libs = tools.collect_libs(self)

    def package_id(self):
        if self.settings.os == "Macos":
            # no os.version so not tied to a minimum deployment target
            del self.info.settings.os.version
            # Vulkan binaries for Mac are compatible with both x86 and armv8
            if self.settings.arch in ("x86_64", "armv8"):
                self.info.settings.arch = "x86_64/armv8"
