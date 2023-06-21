# GLEW package details

# FoundryGL
## CMake
Normal versions of GLEW did not ship with the CMake files. 
This solved an issue with some versions of CMake made its and our config files clash.

For FoundryGL this is not possible as the CMake supplied files request the OpenGL package, 
which is a no go.
So FoundryGL GLEW ships with the CMake config files that include a CMake version check 
and warning of there is a possible issue.
The CMake config files have also been tweeked to allow for multiple setups, which they did not do before.


