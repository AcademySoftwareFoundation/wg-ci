# Boost package details

## User info
The boost package contains a number of Conan `user_info` extensions which can simplify consumption downstream. These represent state that can be set in both Conan and CMake.

None of these are mandatory, but should be seen as helpers to simplify consumption.

The entries are defined per Conan `package_id`, so they are correctly set for the flavour of Boost desired, which is otherwise a fair amount of manual guesswork.

### CMake configuration
The following `user_info` entries may be set:
* `Boost_USE_STATIC_LIBS`
* `Boost_NAMESPACE`
* `Boost_NO_BOOST_CMAKE`
* `Boost_USE_DEBUG_PYTHON`
* `Boost_PYTHON_COMPONENT`

These refer to CMake variables that should be set prior to calling `find_package(boost ...)`. See [the FindBoost docs](https://cmake.org/cmake/help/latest/module/FindBoost.html) for details.

### Compiler configuration
The following `user_info` entry is defined:
* `Boost_COMPILE_DEFINITIONS`

## Consuming
The Boost `test_package` is a good example that uses the `user_info`. The details of interest that you would include in your consuming Conan recipe are:
```python
cmake = CMake(self)
cmake.definitions.update(self.deps_user_info["boost"].vars)
```
and in your package's `CMakeLists.txt` for the target of interest that requires Boost:
```cmake
target_compile_definitions(
  <name of your target>
  PRIVATE
  ${Boost_COMPILE_DEFINITIONS}
)
```
