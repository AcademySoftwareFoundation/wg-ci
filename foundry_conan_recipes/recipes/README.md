# Foundry Conan recipe snapshot

This is a snapshot of a subset of Foundry's Conan 1.x recipes.

It is provided to the community under the Apache 2.0 license.

**CAVEATS:** 
  * The snapshot is provided as a reference point for others looking toward Conan-based solutions.
  * It does not constitute a fully functional, Foundry-supported or Foundry-maintained resource. 
  * It will not work out-of-the-box outside of Foundry's internal ecosystem without alterations to the code. 
  
Notable changes vs the non-public source includes (but is not limited to) the following:
  * Git references are to Foundry's internal Git server for source code to build. However, these are mirrors of publicly available repositories. Some have been patched, but those patches are not provided in this archive.
  * Assets required by some `test_package`s were removed. These include things like `.zip` archives, `.jpg` and `.exr` images. You will need to provide alternative test assets.
  * Some `test_package/*.h|cpp` files were removed. These will require new tests to be authored.
  * No CI scripts to drive automated builds via `config.yml` settings of chains of dependencies is provided with this source drop.

Python 3 is required (>= 3.7).

See `requirements.txt` for additional build-time tooling in Python virtual environments.

