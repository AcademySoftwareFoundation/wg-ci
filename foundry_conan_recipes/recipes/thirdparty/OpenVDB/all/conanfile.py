# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanException
from jinja2 import Environment, FileSystemLoader

class OpenVDBConan(ConanFile):
    name = "OpenVDB"
    settings = "os", "compiler", "build_type", "arch"
    description = "OpenVDB is an open source C++ library comprising a novel hierarchical data structure and a large suite of tools for the efficient storage and manipulation of sparse volumetric data discretized on three-dimensional grids."
    url = "https://github.com/dreamworksanimation/openvdb"
    license = "MPL-2.0"
    author = "DreamWorks Animation"
    revision_mode = "scm"
    generators = "cmake_paths"
    options = {"shared": [True]}
    default_options = {"shared": True}
    package_originator = "External"
    package_exportable = True
    exports_sources = "OpenVDBConfig.cmake.in"

    requires = (
        "Blosc/1.14.3@thirdparty/development",
        "zlib/1.2.11@thirdparty/development",
    )

    def configure(self):
        if tools.Version(self.version) >= '9.0.0':
            # Don't use a shared version of Blosc since it's not used anywhere else
            self.options["Blosc"].shared = False
            self.options["Blosc"].fPIC = True

    def requirements(self):
        if tools.Version(self.version) < '9.0.0':
            # vfxrp 2020 requirements
            self.requires("boost/1.70.0@thirdparty/development")
            self.requires("OpenEXR/2.4.2@thirdparty/development")
            self.requires("tbb/2019_U6@thirdparty/development")
        else:
            if tools.Version(self.version) == '9.0.0':
                # vfxrp 2022 requirements
                self.requires("boost/1.76.0")
            elif tools.Version(self.version) >= '10.0.0':
                # vfxrp 2023 requirements
                self.requires("boost/1.80.0")
            self.requires("imath/3.1.4")
            self.requires("OpenEXR/3.1.4")
            self.requires("tbb/2020_U3")

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_OpenVDB_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")

        cmake.definitions["USE_OPENVDB_PROVIDED_CMAKE_MODULES"] = "OFF"
        cmake.definitions["DISABLE_DEPENDENCY_VERSION_CHECKS"] = "ON"
        cmake.definitions["OPENVDB_BUILD_UNITTESTS"] = "OFF"
        cmake.definitions["OPENVDB_BUILD_PYTHON_MODULE"] = "OFF"
        cmake.definitions["OPENVDB_INSTALL_CMAKE_MODULES"] = "OFF"
        cmake.definitions["MINIMUM_BOOST_VERSION"] = "1.70"
        cmake.definitions["USE_PKGCONFIG"] = "OFF"
        cmake.definitions["OPENVDB_ENABLE_RPATH"] = "OFF"
        cmake.definitions["OPENVDB_BUILD_VDB_PRINT"] = "OFF"
        cmake.definitions["USE_BLOSC"] = "ON"
        cmake.definitions["USE_ZLIB"] = "ON"
        cmake.definitions["USE_LOG4CPLUS"] = "OFF"
        cmake.definitions["USE_EXR"] = "ON"
        cmake.definitions["OPENVDB_CORE_SHARED"] = "ON"
        cmake.definitions["OPENVDB_CORE_STATIC"] = "OFF"

        # Disable all RPATHs so that build machine paths do not appear in binaries.
        cmake.definitions["CMAKE_SKIP_RPATH"] = "1"

        cmake.definitions.update(self.deps_user_info["boost"].vars)

        cmake.configure(
            source_folder=os.path.join(self.source_folder, self._source_subfolder)
        )
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _write_cmake_config_file(self):
        p = os.path.join(self.package_folder, "cmake")
        if not os.path.exists(p):
            os.mkdir(p)

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {}

            if tools.Version(self.version) < "9.0.0":
                data["use_imath"] = "False"
                data["openexr_libs"] = "OpenEXR::Half;OpenEXR::IlmImf"
                data["boost_libs"] = "Boost::math"
                data["boost_components"] = "math"
            else:
                data["use_imath"] = "True"
                data["boost_components"] = "iostreams system"
                data["boost_libs"] = "Boost::iostreams;Boost::system"
                data["openexr_libs"] = "Imath::Imath"
            
            interpreter_template = env.get_template(file_name + ".in")
            interpreter_template.stream(data).dump(os.path.join(self.package_folder, "cmake", file_name))
        
        _configure("OpenVDBConfig.cmake")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self._write_cmake_config_file()


    def package_id(self):
        boost = self.info.requires['boost']
        boost.package_id = boost.full_package_id
