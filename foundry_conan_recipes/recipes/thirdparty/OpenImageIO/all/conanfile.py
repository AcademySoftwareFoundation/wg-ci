# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, CMake

class OpenImageIOConan(ConanFile):
    name = "OpenImageIO"
    license = "BSD-3-Clause"
    author = "Larry Gritz"
    url = "http://www.openimageio.org/"
    description = "OpenImageIO is a library for reading and writing images, and a bunch of related classes, utilities, and applications."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    generators = "cmake_paths"
    exports_sources = "*.cmake.in"
    no_copy_source = False
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__cmake = None

    def __get_boost_version(self):
        if tools.Version(self.version) < '2.3.21.0':
            return 'boost/1.76.0'
        else:
            return 'boost/1.80.0'

    def requirements(self):
        self.requires('PNG/[~1.6.37]@thirdparty/development')
        self.requires('zlib/1.2.11@thirdparty/development')
        self.requires(self.__get_boost_version())
        self.requires('JPEG/9e')
        self.requires('OpenEXR/3.1.4')
        self.requires('fmt/8.1.1')
        self.requires('imath/3.1.4')
        self.requires('libtiff/4.3.0')

    def build_requirements(self):
        self.build_requires('robin-map/0.6.3')  # Header-only.

    @property
    def _library_name(self):
        suffix = "" if self.options.shared else "_static"
        libname = "OpenImageIO_Foundry" if self.settings.os == "Windows" else "libOpenImageIO_Foundry"
        library = "{}{}".format(libname , suffix)
        return library

    @property
    def _library_util_name(self):
        suffix = "" if self.options.shared else "_static"
        libname = "OpenImageIO_Util_Foundry" if self.settings.os == "Windows" else "libOpenImageIO_Util_Foundry"
        library = "{}{}".format(libname , suffix)
        return library

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        # When OIIO is reconfigured, its CMake cache gets wrongly invalidated, and several targets
        # are bound to be rebuilt. To prevent unnecessary rebuilds, the `cmake` object will be
        # cached between the building and the packaging stages. See TP 504957.
        if self.__cmake is not None:
            return self.__cmake

        cmake = CMake(self)
        self.__cmake = cmake

        cmake.definitions["CMAKE_PROJECT_OpenImageIO_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")

        cmake.definitions["OIIO_NAMESPACE"] = "OpenImageIO_Foundry"
        cmake.definitions["OIIO_BUILD_TOOLS"] = "OFF"
        cmake.definitions["OIIO_BUILD_TESTS"] = "OFF"
        cmake.definitions["EMBEDPLUGINS"] = "ON"
        cmake.definitions["LINKSTATIC"] = "OFF" if self.options["boost"].shared else "ON"
        cmake.definitions["USE_CPP11"] = "ON"
        cmake.definitions["USE_FFMPEG"] = "OFF"
        cmake.definitions["USE_FREETYPE"] = "OFF"
        cmake.definitions["USE_FIELD3D"] = "OFF"
        cmake.definitions["USE_GIF"] = "OFF"
        cmake.definitions["USE_LIBRAW"] = "OFF"
        cmake.definitions["USE_NUKE"] = "OFF"
        cmake.definitions["USE_OCIO"] = "OFF"
        cmake.definitions["USE_OPENCV"] = "OFF"
        cmake.definitions["USE_OPENJPEG"] = "OFF"
        cmake.definitions["USE_PYTHON"] = "OFF"
        cmake.definitions["USE_QT"] = "OFF"
        cmake.definitions["STOP_ON_WARNING"] = "OFF"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        # Avoid building external dependencies from source if our conanified packages cannot be
        # found.
        cmake.definitions['BUILD_MISSING_FMT'] = False
        cmake.definitions['BUILD_MISSING_ROBINMAP'] = False

        # Test data set not at hand; unit tests will be disabled also in 2.0.0.0+.
        cmake.definitions['BUILD_TESTING'] = False

        # Our custom CMake config file expects no "_d" suffix, which OIIO 2 would add otherwise.
        if self.settings.build_type == 'Debug':
            cmake.definitions['CMAKE_DEBUG_POSTFIX'] = ''

        # Since OIIO 2, an official CMake option is provided by OIIO.
        libsuffix_option_name = 'OIIO_LIBNAME_SUFFIX'

        if self.options.shared:
            cmake.definitions["BUILDSTATIC"] = "OFF"
            cmake.definitions[libsuffix_option_name] = "_Foundry"
        else:
            cmake.definitions["BUILDSTATIC"] = "ON"
            cmake.definitions[libsuffix_option_name] = "_Foundry_static"
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.settings.os == "Windows":
            cmake.definitions["OPENEXR_USE_STATIC_LIBS"] = "OFF" if self.options["OpenEXR"].shared else "ON"

        # Use the Boost package info to define Boost definitions.
        cmake.definitions.update(self.deps_user_info["boost"].vars)

        if self.options.shared and self.settings.os == "Macos":
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        is_linux = self.settings.os == "Linux"
        tokens = {}
        if self.options.shared:
            tokens["OPENIMAGEIO_LIBTYPE"] = "SHARED"
            tokens["OPENIMAGEIO_LIBEXT"] = ".dll" if is_windows else ".so" if is_linux else ".dylib"
        else:
            tokens["OPENIMAGEIO_LIBTYPE"] = "STATIC"
            tokens["OPENIMAGEIO_LIBEXT"] = ".lib" if is_windows else ".a"

        tokens["OPENIMAGEIO_LIBNAME"] = self._library_name
        tokens["OPENIMAGEIO_LIBNAME_UTIL"] = self._library_util_name
        tokens["CONAN_BOOST_VERSION"] = self.deps_cpp_info["boost"].version

        config_in_path = os.path.join(self.source_folder, "OpenImageIOConfig.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(config_out_dir, "OpenImageIOConfig.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        # The auto-generated CMake/pkg-config files include absolute, hardcoded paths. Our
        # custom CMake config file does a better job, and will be used instead.
        self.output.info('Removing auto-generated CMake/pkg-config files...')
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

        self._write_cmake_config_file()

    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = ["OpenImageIO"]

        if not self.options.shared:
            self.cpp_info.defines = ["OIIO_STATIC_BUILD"]

    def package_id(self):
        boost = self.info.requires['boost']
        boost.package_id = boost.full_package_id
