# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os, semver
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration, ConanException
from jinja2 import Environment, FileSystemLoader


class UsdConan(ConanFile):
    name = "USD"
    license = "Apache-2.0"
    author = "Pixar"
    url = "https://github.com/PixarAnimationStudios/USD"
    description = "Universal Scene Description (USD) is an efficient, scalable system for authoring, reading, and streaming time-sampled scene description for interchange between graphics applications."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "imaging": [True, False],
        "python_bindings": [True, False],
        "namespace": "ANY",
        "openvdb": [True, False],
        "GLBackend" : ["OpenGL" ,"FoundryGL"],
        "materialx": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "imaging": True,
        "python_bindings": False,
        "namespace": None,
        "openvdb": True,
        "GLBackend":"OpenGL",
        "materialx": False,
    }
    exports_sources = ("cmake/*", "bootstrap.py.in")
    no_copy_source = True
    short_paths = True
    generators = "cmake_paths"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _useFoundryGLBackend(self):
        """ Detect FoundryGL specific GLBackend option """
        return self.options.GLBackend == "FoundryGL"

    @property
    def _useOpenGLBackend(self):
        """ Detect non-default GLBackend option """
        return self.options.GLBackend == "OpenGL"

    @property
    def _checkout_folder(self):
        return "{}_src".format(self.name)

    @property
    def _run_unit_tests(self):
        return "USD_RUN_UNITTESTS" in os.environ

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _addOpenImageIOPlugin(self):
        if self.options.imaging:
            return True
        return False

    @property
    def _enableOpenVDBSupport(self):
        if self.options.openvdb and self.options.imaging:
            return True
        return False

    @property
    def _requires_dynamic_boost(self):
        # USD only supports dynamic Boost Python, see, for example
        #  https://github.com/PixarAnimationStudios/USD/issues/1087
        #  https://github.com/PixarAnimationStudios/USD/issues/407
        return self.options.python_bindings

    @property
    def _is_vfx23(self):
        """ Decides whether to use VFX23 based library versions."""
        return self.version in ["22.05-vfx23"]

    def _get_tbb_version(self):
        return "tbb/2020_U3"

    def _get_boost_version(self):
        if self._is_vfx23:
            return "boost/1.80.0"
        else:
            return "boost/1.76.0"

    def _get_pyside_version(self):
        return "PySide2/5.15.2.1"

    def _get_alembic_version(self):
        return "Alembic/1.8.3"

    def _get_oiio_version(self):
        if self._is_vfx23:
            return "OpenImageIO/2.3.21.0"
        else:
            return "OpenImageIO/2.3.13.0"

    def _get_open_exr_version(self):
        return "OpenEXR/3.1.4"

    def _get_vdb_version(self):
        if self._is_vfx23:
            return "OpenVDB/10.0.1"
        else:
            return "OpenVDB/9.0.0"

    def _get_opensubdiv_version(self):
        if self._is_vfx23:
            return "OpenSubdiv/3.5.0@thirdparty/development"
        else:
            return "OpenSubdiv/3.4.3@thirdparty/development"

    def _is_python3_enabled(self):
        if not 'Python' in self.deps_cpp_info.deps:
            return False

        return tools.Version(self.deps_cpp_info['Python'].version) >= '3'

    def configure(self):
        if not self._useOpenGLBackend:
            self.options["GLEW"].GLBackend = self.options.GLBackend
            self.options["OpenSubdiv"].GLBackend = self.options.GLBackend
            self.options["Qt"].GLBackend = self.options.GLBackend # Needed for PySide2

    def validate(self):
        try:
            if not self.options.fPIC:
                raise ConanInvalidConfiguration(
                    "USD currently enforces the use of fPIC in their build scripts. Grep for POSITION_INDEPENDENT_CODE"
                )
        except ConanException as exception:
            self.output.warn("Ignoring: {}".format(exception))

        if self.options.python_bindings and not self.options['boost'].python_version:
            raise ConanInvalidConfiguration(
                "USD Python bindings require specifying the boost:python_version option to something other than None."
            )


    def requirements(self):
        self.requires(self._get_tbb_version())
        self.requires(self._get_boost_version())
        if self.options.imaging:
            self.requires("GLEW/1.13.0@thirdparty/development")
            self.requires(self._get_open_exr_version()) # required at runtime by Alembic and OIIO
        if self._enableOpenVDBSupport:
            self.requires(self._get_vdb_version())
        if self.options.python_bindings:
            if self.options.imaging:
                self.requires(self._get_pyside_version())
        if self._useFoundryGLBackend:
            self.requires("foundrygl/0.1@common/development")
        if self.options.materialx:
            self.requires("MaterialX/1.38.6")

    def build_requirements(self):
        if self.options.imaging:
            self.build_requires(self._get_opensubdiv_version())
            self.build_requires(self._get_alembic_version())
        if self._addOpenImageIOPlugin:
            self.build_requires(self._get_oiio_version())

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _python_path_environment(self):
        env = {}
        if self.options.python_bindings:
            env["PYTHONPATH"] = []
            env["PYTHONPATH"].append(os.path.join(self.build_folder, "site-packages")) # see jinja2-config.cmake
            if self.options.imaging:
                if self.settings.os == "Windows":
                    # TODO(AH) - can't use PySide2's exported site_package on Windows as it's wrong
                    env["PYTHONPATH"].append(os.path.join(self.deps_cpp_info["PySide2"].rootpath, "lib", "site-packages"))
                    env["PATH"] = [
                        os.path.join(self.deps_cpp_info["Qt"].rootpath, "bin"),
                        os.path.join(self.deps_cpp_info["PySide2"].rootpath, "bin"),
                        self.deps_cpp_info["Python"].rootpath
                    ]
                else:
                    env["PYTHONPATH"].append(self.deps_user_info["PySide2"].site_package)
                    env_var = "LD_LIBRARY_PATH" if self.settings.os == "Linux" else "DYLD_FRAMEWORK_PATH"
                    env[env_var] = [
                        os.path.join(self.deps_cpp_info["PySide2"].rootpath, "lib"),
                        os.path.join(self.deps_cpp_info["Qt"].rootpath, "lib")
                    ]
        return env

    def _get_library_naming_definitions(self):
        definitions = {}
        # Set Lib Prefix
        lib_prefix = "fn"
        if self.settings.os != "Windows":
            lib_prefix = "lib"+lib_prefix
        definitions["PXR_LIB_PREFIX"] = lib_prefix
        return definitions

    def _get_namespace_definitions(self):
        ns_definitions = {}
        if self.options.namespace:
            ns_definitions["PXR_ENABLE_NAMESPACES"] = "ON"
            namespace = str(self.options.namespace)
            lowercase_namespace = namespace.lower()
            # Setup namespace for USD Python Package
            if self.options.python_bindings:
                ns_definitions["PXR_PY_PACKAGE_NAME"] = "{ns}pxr".format(
                    ns=lowercase_namespace)
            # Set PluginPath name (used to add plugins to the USD plugin search paths)
            ns_definitions["PXR_OVERRIDE_PLUGINPATH_NAME"] = "{ns}PXR_PLUGINPATH".format(
                ns=namespace.upper())
            # Setup internal and external namespaces
            ns_definitions["PXR_SET_EXTERNAL_NAMESPACE"] =  \
                "{ns}pxr".format(ns=lowercase_namespace) # default is pxr
            # Split by `-` first to remove potential suffix on version
            split_version = self.version.split("-")[0].split(".")
            version_year = split_version[0]
            version_month = split_version[1]
            ns_definitions["PXR_SET_INTERNAL_NAMESPACE"] = \
                "{ns}Internal_v{year}_{month}".format(
                    ns=namespace,
                    year=version_year,
                    month=version_month
                )
        return ns_definitions

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_usd_INCLUDE"] = os.path.join(
            self.install_folder, "conan_paths.cmake"
        )
        # see USD/cmake/defaults/Options.cmake
        cmake.definitions["PXR_USE_USD_CMAKE_MODULES"] = "OFF" # prefer Foundry ways to find dependents
        cmake.definitions["CMAKE_PREFIX_PATH"] = os.path.join(self.source_folder, "cmake")
        cmake.definitions["PXR_STRICT_BUILD_MODE"] = "OFF"
        cmake.definitions["PXR_VALIDATE_GENERATED_CODE"] = "ON"
        cmake.definitions["PXR_HEADLESS_TEST_MODE"] = "OFF"
        cmake.definitions["PXR_BUILD_TESTS"] = "ON" if self._run_unit_tests else "OFF"
        cmake.definitions["PXR_BUILD_IMAGING"] = "ON" if self.options.imaging else "OFF"
        cmake.definitions["PXR_BUILD_EMBREE_PLUGIN"] = "OFF"
        cmake.definitions["PXR_BUILD_OPENIMAGEIO_PLUGIN"] = "ON" if self._addOpenImageIOPlugin else "OFF"
        cmake.definitions["PXR_BUILD_OPENCOLORIO_PLUGIN"] = "OFF"
        cmake.definitions["PXR_BUILD_USD_IMAGING"] = "ON" if self.options.imaging else "OFF"
        cmake.definitions["PXR_BUILD_USDVIEW"] = "ON" if self.options.imaging and self.options.python_bindings else "OFF"
        cmake.definitions["PXR_BUILD_KATANA_PLUGIN"] = "OFF"
        cmake.definitions["PXR_BUILD_MAYA_PLUGIN"] = "OFF"
        cmake.definitions["PXR_BUILD_ALEMBIC_PLUGIN"] = "ON" if self.options.imaging else "OFF"
        cmake.definitions["PXR_BUILD_DRACO_PLUGIN"] = "OFF"
        cmake.definitions["PXR_BUILD_HOUDINI_PLUGIN"] = "OFF"
        cmake.definitions["PXR_BUILD_PRMAN_PLUGIN"] = "OFF"
        cmake.definitions["PXR_BUILD_DOCUMENTATION"] = "OFF"
        cmake.definitions["PXR_ENABLE_GL_SUPPORT"] = "ON" if self.options.imaging else "OFF"
        cmake.definitions["PXR_ENABLE_PYTHON_SUPPORT"] = "ON" if self.options.python_bindings else "OFF"
        cmake.definitions["PXR_ENABLE_OPENVDB_SUPPORT"] = "ON" if self._enableOpenVDBSupport else "OFF"
        cmake.definitions["PXR_ENABLE_MATERIALX_SUPPORT"] = "ON" if self.options.materialx else "OFF"
        cmake.definitions["PXR_USE_PYTHON_3"] = "ON" if self._is_python3_enabled() else "OFF"
        cmake.definitions["PXR_ENABLE_MULTIVERSE_SUPPORT"] = "OFF"
        cmake.definitions["PXR_ENABLE_HDF5_SUPPORT"] = "OFF"
        cmake.definitions["PXR_ENABLE_OSL_SUPPORT"] = "OFF"
        cmake.definitions["PXR_ENABLE_PTEX_SUPPORT"] = "OFF"
        cmake.definitions["PXR_MAYA_TBB_BUG_WORKAROUND"] = "OFF"
        cmake.definitions["PXR_ENABLE_NAMESPACES"] = "ON"
        cmake.definitions["PXR_BUILD_MONOLITHIC"] = "OFF"
        cmake.definitions["PXR_ENABLE_METAL_SUPPORT"] = "ON"
        cmake.definitions.update(self.deps_user_info["boost"].vars)
        # disable all RPATHs so that build machine paths do not appear in binaries
        cmake.definitions["CMAKE_SKIP_RPATH"] = "1"
        if not self.options.shared:
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"
        cmake.definitions.update(self._get_library_naming_definitions())
        if self.options.namespace:
            ns_definitions = self._get_namespace_definitions()
            for key, value in ns_definitions.items():
                cmake.definitions[key] = value
        env = self._python_path_environment()
        if env:
            self.output.info("Running CMake configure with the following environment variables:\n{}".format(env))
        with tools.environment_append(env):
            cmake.configure(
                source_folder=os.path.join(self.source_folder, self._checkout_folder)
            )
        return cmake, env

    def build(self):
        cmake, env = self._configure_cmake()
        with tools.environment_append(env):
            cmake.build()


    def _write_bootstrap_py_file(self, cmake):

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {}
            data["PXR_OVERRIDE_PLUGINPATH_NAME"] = "PXR_PLUGINPATH_NAME"
            if self.options.namespace:
                data["PXR_OVERRIDE_PLUGINPATH_NAME"] = \
                    str(cmake.definitions["PXR_OVERRIDE_PLUGINPATH_NAME"])
            interpreter_template = env.get_template(file_name + ".in")
            interpreter_template.stream(data).dump(os.path.join(self.package_folder, file_name))

        _configure("bootstrap.py")

    def package(self):
        cmake, _ = self._configure_cmake()
        cmake.install()
        self._write_bootstrap_py_file(cmake)
        if self._run_unit_tests:
            # USD currently requires to run tests after install
            cmake.test(output_on_failure=True)

    def package_info(self):
        ns_definitions = self._get_namespace_definitions()
        self.user_info.PXR_PY_PACKAGE_NAME = ns_definitions.get("PXR_PY_PACKAGE_NAME","pxr")

    def package_id(self):
        boost = self.info.requires['boost']
        boost.package_id = boost.full_package_id
