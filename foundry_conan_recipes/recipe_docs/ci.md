# Recipe Continuous Integration

> **_Note_**: GitLab CI is used both for building topic branches (artifacts are emphemeral) and also post-merge to the default branch where a build will be uploaded to the production remote on Artifactory

<!-- using MarkDown All In One extension in VSCode for the TOC -->
- [Recipe Continuous Integration](#recipe-continuous-integration)
  - [GitLab CI](#gitlab-ci)
  - [Frequency of CI pipeline launches](#frequency-of-ci-pipeline-launches)
    - [Web interface](#web-interface)
    - [Known issues](#known-issues)
      - [Raw output](#raw-output)
      - [Unicode characters in commit messages](#unicode-characters-in-commit-messages)
      - [Intermittent cleaning failures upon startup](#intermittent-cleaning-failures-upon-startup)
      - [Older Conan versions not installable on Apple Silicon](#older-conan-versions-not-installable-on-apple-silicon)
  - [pipelinecli](#pipelinecli)
    - [Build tool versioning](#build-tool-versioning)
      - [Choosing tool versions](#choosing-tool-versions)
    - [Running locally](#running-locally)
      - [Debug logging](#debug-logging)
    - [Packages built](#packages-built)
      - [Multi-recipe topic branches](#multi-recipe-topic-branches)
      - [Testing topic branch builds downstream](#testing-topic-branch-builds-downstream)
      - [Lifetime of per-branch Artifactory repositories](#lifetime-of-per-branch-artifactory-repositories)
    - [GitLab pipeline job names](#gitlab-pipeline-job-names)
      - [Order of packages built](#order-of-packages-built)
      - [Clean merge history](#clean-merge-history)
    - [pipelinecli versions](#pipelinecli-versions)
    - [Additional command line control](#additional-command-line-control)
    - [pipelinecli configuration](#pipelinecli-configuration)
      - [Proprietary thirdparty licenses](#proprietary-thirdparty-licenses)
      - [Platforms to build](#platforms-to-build)
      - [Build types to build](#build-types-to-build)
      - [GitLab runner tags per platform](#gitlab-runner-tags-per-platform)
      - [GitLab runner shells](#gitlab-runner-shells)
      - [Active toolchains](#active-toolchains)
      - [Toolchain Versions](#toolchain-versions)
      - [Conan configuration branch per profile](#conan-configuration-branch-per-profile)
  - [Package variations](#package-variations)
    - [Simple variant sets](#simple-variant-sets)
      - [Option variations](#option-variations)
      - [Platform variations](#platform-variations)
      - [Build type variations](#build-type-variations)
      - [Configuration](#configuration)
        - [`build_timeout`](#build_timeout)
        - [`conan_request_timeout`](#conan_request_timeout)
        - [`conan_config_branch`](#conan_config_branch)
        - [`pkgref_namespace`](#pkgref_namespace)
        - [`pkgref_name`](#pkgref_name)
          - [Requirements:](#requirements)
      - [Inclusion/exclusion from active toolchains/profiles](#inclusionexclusion-from-active-toolchainsprofiles)
        - [`only_profiles`](#only_profiles)
        - [`excluded_profiles`](#excluded_profiles)
        - [`excluded_toolchains`](#excluded_toolchains)
    - [Named variant sets](#named-variant-sets)
      - [Hidden named variant sets](#hidden-named-variant-sets)
  - [CMake error logs saved for retrospection](#cmake-error-logs-saved-for-retrospection)
  - [Package build environments](#package-build-environments)
  - [Skipping CI](#skipping-ci)
    - [Disabling CI entirely on a branch](#disabling-ci-entirely-on-a-branch)

## GitLab CI
The [`.gitlab-ci.yml`](../.gitlab-ci.yml) file in the root of the recipes repository is the entry point to GitLab's own CI system.

This file is kept intentionally simple, and unaware of the business logic involved in building Conan packages. This logic is instead implemented in an external Python pip package called `pipelinecli`.

## Frequency of CI pipeline launches
Whenever a `git push` is made to a topic branch in the repository, a pipeline will be launched.

If multiple pushes are made to a branch while pipelines are running, older pipelines will be automatically cancelled by GitLab, with only the pipeline for the most recent push continuing. This ensures that only the latest code is being built, and not wasting build resources on out-dated source.

See also [skipping CI](#skipping-ci) if it's not desirable to have a pipeline immediately upon pushing, e.g. perhaps it's a long build that you want to defer until a less busy time later.

### Web interface
Use the [web interface](https://a_gitlab_url/libraries/conan/recipes/-/pipelines) to the CI system to view progress of your builds.

You can also use the GitLab web interface to launch a build of your topic branch without needing to do a push. Use the "Run Pipeline" button in the link above, and select your topic branch on the drop down on the form shown. See also the [GitLab documentation](https://docs.gitlab.com/ee/ci/pipelines/#run-a-pipeline-manually).

Using "Run Pipeline" on the default branch is discussed later.

### Known issues
#### Raw output
Sometimes, the styled web interface for build output does not show everything you would expect to see. More often than not, this seems to be for Windows builds. In order to see the full log, either add `/raw` to the end of the job URL, or click on the toolbutton at the top-right of the job output window with the tooltip "Show complete raw".

See
* https://gitlab.com/gitlab-org/gitlab/-/issues/210319

#### Unicode characters in commit messages
On Windows (using the Powershell runner, which we do), a commit message containing unicode characters will fail the build in the GitLab scripts. Linux and Mac runners seem to be unaffected.

Please use ASCII characters only in your commit messages. While working in topic branches, you can rewrite your commit messages using interactive `git rebase`.

See
* https://gitlab.com/gitlab-org/gitlab-runner/-/issues/10123
* https://gitlab.com/gitlab-org/gitlab-runner/-/issues/27383

#### Intermittent cleaning failures upon startup
There is a [known bug](https://gitlab.com/gitlab-org/gitlab-runner/-/issues/3185) in the GitLab runners which can cause the initial checkout phase to fail. This happens very early on, so won't waste many cycles. You may see something like this, with the warning and error as shown:
```
Getting source from Git repository
00:13
Fetching changes with git depth set to 50...
Reinitialized existing Git repository in /Users/builder/builds/LrG4SNs3/0/libraries/conan/recipes/.git/
Checking out 81ed63f5 as mf/boost_windows_failures...
warning: failed to remove 5-18243-88418/.conan/data/USD/21.05-metal/thirdparty: Directory not empty
```
Simply restarting the job seems to resolve the problem.

#### Older Conan versions not installable on Apple Silicon
If you see an error right at the start of an Apple Silicon build while installing Conan which includes
```
      build/temp.macosx-10.9-universal2-3.10/_openssl.c:575:10: fatal error: 'openssl/opensslv.h' file not found
      #include <openssl/opensslv.h>
               ^~~~~~~~~~~~~~~~~~~~
      1 error generated.
      error: command '/usr/bin/clang' failed with exit code 1
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for cryptography
```
then the Conan version is too old.

As the version in the global `requirements.txt` is quite new, the likely reason for this is that there is now a redundant `build-environment` section of the recipe's `conandata.yml`. This can be removed, if all the requirements are satisfied elsewhere.

## pipelinecli
This is an internal Python tool that performs analysis on recipe Git topic branches to determine which Conan packages have been affected by commits, and thus need to be built.

There are three modes of operation:

1. `pipelinecli conan ci gitlab ...` which is invoked by `.gitlab-ci.yml` and generates a YAML file that GitLab CI consumes in a child pipeline.
   1. For changes to recipe files that would affect the packages to be built, the generated YAML file executes `conan create` commands for each defined variation of each changed package, subsequently calling `conan upload` to a _temporary_ Artifactory repository to account for dependencies between those rebuilt packages. The Artifactory repository used is named after the topic branch. Each Conan package variation _can_ be built on a different GitLab CI runner (build machine) that matches the required tags, thus allowing for maximum parallelism during package builds.
   2. For changes to files _only_ in a recipe's `test_package` directory, jobs using `conan test` will be generated in the YAML instead. When executed, this command will download the _existing_ library packages from Artifactory and run the modified tests against them. Modifications to the `test_package` do not change the contents nor hashes of the library builds, which is why this does not perform the full build. However, if commits in the topic branch are detected to the corresponding library files, the full `conan create` workflow will be used instead.
   3. `pipelinecli` checks all variants for whether their `package_id` exists on Artifactory first. If they do already exist, they will not be built as part of CI, since this is otherwise wasteful on build resources. If they don't exist, e.g. because say a change to the `config.yml` for the package is _additive_, or only affects a subset of variants, then only those missing will be built. The top-level job in the pipeline contains output indicating which variants already exist.
2. `pipelinecli conan ci local ...` which is run from a developer machine, and produces a shell script executing the same `conan create`/`conan test` commands as the remote GitLab CI would run, except only for the current platform. Packages are written to an isolated Conan local cache using an isolated Python 3 virtual environment, to ensure as much independence from your development environment as possible. Bash, batch and Powershell formats are provided.
3. The GitLab web interface "Run Pipeline" form is used to launch a pipeline on the _default_ branch, as well as topic branches. This workflow for the default branch is useful when _no changes_ are needed to recipes, but there may be missing `package_id`s for the latest recipe revisions, needing to be built. For example, when toolchains are added with associated changes to profile settings. There are variables on the web form to provide values for in order to launch the desired builds:
   1. `CONFIG_DIRS`: A space separate list of directories for the `config.yml` files of the packages of interest to build. The order provided is the order in which the packages will be scheduled. (Default branch only)
   2. `UPLOAD_PACKAGES`: An integer, defaulting to 0, specifying whether to upload the results of builds. Hence, by default, it can be used to validate builds but not publish. Set to any non-zero integer to enable uploads. (Default branch only)
   3. `CASCADE_UPSTREAM`: An integer, defaulting to 0, specifying whether to consider all upstream dependencies in the pipeline starting from those specified in `CONFIG_DIRS`. This will essentially fill in the gaps for any missing package_ids to satisfy the package(s) requested. Set to any non-zero integer to enable cascading. This has the potential to create a pipeline that exceeds GitLab's limitations; reduce scope if it does. (Default branch only)
   4. `EMPTY_REMOTE`: An integer, defaulting to 0, specifying whether to empty the temporary CI Conan remote of packages before building. Set to any non-zero integer to enable emptying. (Topic branches only; is ignored for the default branch.)

### Build tool versioning
To align automated build environments with developer environments, `pipelinecli` creates a Python virtual environment for _each_ GitLab build job, from the following, in this order, using `pip install`:

1. Global `requirements.txt` file in the root of the repository (copes with the file not existing)
2. Per recipe `build-environment` map in the recipe `conandata.yml` (copes with this missing) *DEPRECATED*
3. A `thirdparty/<name>/requirements.txt` recipe-local requirements (copes with this file not existing)

As noted, the `conandata.yml` approach is deprecated, and will be removed during maintenance.

Ideally, the global `requirements.txt` will be on modern enough versions of Conan, CMake, Ninja to satisfy all the recipe builds. The recipe-local requirements is the place to put local overrides. Note that this local override is not designed to be per-version.

A developer workflow, to use an aligned build environment (in terms of Python packages at least) with canonical build machines, is to do exactly the same as the tooling, `pip install` the requirements files. (This is one reason that the `conandata.yml` approach is deprecated.)

#### Choosing tool versions
The versions specified in the global `requirements.txt` will be assessed at a regular interval, and updated where necessary with community agreement. Ideally, this would be backed with some regression testing, but is yet to be developed.

Version numbers of pip packages will be exact in requirements files, rather than a range, so that it is a consistent environment for all users.

### Running locally
In order to run pipelinecli locally, you need to either install a wheel (from our Artifactory, see `.gitlab-ci.yml` for how to do that), or clone the Git repository. To clone, use
```bash
git clone git@a_gitlab_url:devops/pipelinecli.git -b v1.x
```
and then
```bash
pip install -e .
```
in the cloned directory to install it to your local site packages as a development version (highly recommend using Python virtual environments). You will be able to run `pipelinecli` in your terminal after that.

Running `pipelinecli -h` will provide more information.

#### Debug logging
pipelinecli uses Python logging internally. If you set the environment variable `LOGLEVEL` to `DEBUG`, additional output will be observed on the console. This can also be applied in topic branches in `.gitlab-ci.yml` if additional information is needed about a subsequent CI run.

### Packages built
Package binaries are uploaded to a per-topic-branch Artifactory repository. These binaries are persisted until either a) a change causes a revision change (thus needing to remove stale packages), or b) a pipeline is started explicitly with the `EMPTY_REMOTE` variable set to non-zero via the web UI.

A rebase against the default branch would be considered a revision change for any commits already touching recipe files, since SHAs are changed.

If changes are made that would not cause a revision change, then a pipeline only performs incremental updates to its temporary repository.

#### Multi-recipe topic branches
You can make changes to more than one recipe in a topic branch. See [order of packages built](#order-of-packages-built) for more details.

The persistence of the temporary Artifactory repository should help reduce overall build time on each push, assuming nothing changes the revisions of upstream recipes modified earlier on the topic branch.

#### Testing topic branch builds downstream
Since builds are persisted in an Artifactory repository specific to your topic branch, you may add this repository as a new Conan remote to your local cache, and find the packages on that remote in preference over others.
```
conan remote add my_ci_packages <Artifactory URL> --insert
```
The `--insert` argument is to place the specified remote first, since Conan searches remotes in the order they have been provided. See the `remotes.json` file in your Conan local cache.

This means that you can test WIP packages in consumers outside of the thirdparty recipe system, without a) changing their package reference namespace, or b) needing to upload them to the production Conan remote on Artifactory.

The URL to use can be found in the log on the top-most job for your GitLab CI pipeline.

#### Lifetime of per-branch Artifactory repositories
There is no automated mechanism for deleting the temporary Artifactory repositories once their associated Git branches have been deleted, for example after a successful merge request merge, or just after deleting a branch no longer needed.

However, a process is available, which is exposed as a scheduled pipeline job, so developers do not need to include this in their merge request workflow. It should not be assumed, however, that an Artifactory repository for a topic branch continues to exist long after the associated branch has gone.
### GitLab pipeline job names
The generated child pipeline contains a job for each configuration of each variant of each package that needs to be built. The job name consists of various components identifying the build, including the package name, version, build type, variant name. It also ends in a hexadecimal hash. This hash is the MD5 of the string of options that would be passed to Conan commands. This is used instead of the full string to reduce the length of the job name below the GitLab limit of 255 characters.

Although this MD5 hash of the options is less readable than the string itself, you can spot patterns when the same option string has been used across variants, and you can look into the build log for the Conan commands that the actual options string has been provided.

Currently in GitLab, there is no mechanism for providing an alternative label for a job.

#### Order of packages built
Currently, the order of packages built is a naive algorithm that aligns with the _commit order to packages_ in the topic branch. Once a package is scheduled to build from a commit to its files, the package is never rescheduled, so the relative order of the first commit to a package compared to what depends on it matters. If this incorrectly models the dependency order required by Conan, please reorder your commits via rebasing so that the changes to packages occur in downstream order.

#### Clean merge history
Since all commit history in a topic branch is considered, it is passed through a sanity check. This currently checks for:
* changes to files added to the topic branch and subsequently removed, and
* modifications to files made and subsequently reverted in the topic branch.

The goal is to have a clean history upon merge, so that the default branch does not have redundant commits that will confuse any regression when checking history or blame. This is automated because manually examining all commits in a merge request is tedious.

If any changes are detected that fail any of the tests, the first stage of CI fails with an explaination in the error message.

Ideally, commits would then be cleaned up, usually by rebasing, but to allow 'I'm in the zone', you may temporarily suppress the error (dropping it down to a warning) by adding `--suppress-commit-sanitise-error` to the `pipelinecli conan ci gitlab` command in your topic branch's `.gitlab-ci.yml`.

### pipelinecli versions
pipelinecli is versioned following guidelines in [PEP440](https://www.python.org/dev/peps/pep-0440/). The current version of pipelinecli in use is embedded into the `.gitlab-ci.yml` file. This can be changed in recipe topic branches in order to test new features/algorithms.

pipelinecli versions use tags from its Git repository as a baseline version (e.g. `1.2.3`), and either a commit count following the most recent tag (e.g. `1.2.3.dev5`), or a branch name for new development (e.g. `1.2.3.dev0+my.dev.work`).

### Additional command line control
On the GitLab CI invocation, there are some additional command line switches that control the generated runner scripts. These are quite tightly coupled into build machine setup or Conan configurations, and/or plans for changing them.
* `--win-subst-drive` - specify the drive letter to use on Windows drive substitution for short paths; defaults to `T` for consistency with older Jenkins build machines
* `--disable-win-subst-drive` - specify to disable Windows drive substitution - this is for testing purposes only, and not recommended to use
* `--disable-profile` - a wildcarded expression to disable scheduling builds for any matching Conan profiles
* `--prefer-profile-tags` - specify to prefer using GitLab CI runner tags from profile prefixes; otherwise use toolchain versions
* `--setup-win-toolchain` - specify so that generated runner scripts setup the Windows toolchain; otherwise assume it's in the runner environment
* `--setup-linux-toolchain` - specify so that generated runner scripts setup the Linux toolchain; otherwise assume it's in the runner environment

### pipelinecli configuration
pipelinecli has a configuration file associated with it, which can be used to pass extra information when it is executed. By default this is the `.pipeline-config` file.

The format of this file follows an INI file format of sections with key/value pairs to configure things. The configurable sections will be detailed below.

#### Proprietary thirdparty licenses
This section is used to set the url and branch of the repo to be fetched when validating proprietary thirdparty licenses, this section has the following format:
```
[spdx]
extra-licenses-repo-url = [REPO_URL]
extra-licenses-repo-branch = [REPO_BRANCH]
```
In the default recipe branch, the `url` and `branch` shall be set to `git@a_gitlab_url:libraries/conan/spdx-licences-proprietary.git` and `master` respectively, but can be used to point elsewhere in topic branches.

#### Platforms to build
The section `platforms` defines an `active` key with a list of platform/architecture names to build for. These platforms are used in many aspects of the CI build, not only to determine the toolchains in use in this file, but also to form part of the Conan profile filenames.

#### Build types to build
The section `build-types` defines an `active` key with a list of the CMake build types to build packages for. This is used to form Conan profile filenames.

#### GitLab runner tags per platform
The section `platform-gitlab-runner-tags` defines a key per platform (as defined above) each specifying a list of tags to use to help select runners in GitLab CI.

#### GitLab runner shells
The section `gitlab-runner-shells` defines a key per platform (as defined above) each specifying the name of the shell that the GitLab runner for that platform is using. The name must match a class name in `pipelinecli`. This determines the language used to generate runner scripts for builds that are compatible with the runners.

#### Active toolchains
There are sections with a `toolchains-` prefix for each of the active platforms also defined in this file.

These sections define a mapping between active toolchain versions and their corresponding Conan profiles, identified by the prefix to the filenames in your local cache.

The uses of the keys and values in this section are two fold:
1) to form part of the Conan profile filename
2) as another tag to select GitLab runners

For example:
```
[toolchains-win]
vs2017 = ["vfx20"]
vs2019 = ["design21"]
```
defines two active toolchain versions for Windows:
1) VisualStudio 2017, which uses Conan profiles starting with vfx20
2) VisualStudio 2019, which uses Conan profiles starting with design21

Each toolchain for a platform is included when `pipelinecli` builds the scheduled matrix of `conan create` calls for each package.

Although each toolchain is considered in turn by default, the tooling, `pipelinecli` and `jenkins-bridge` do allow some level of filtering on the command line to support machine availability. Alternatively, this can be used to tweak which builds are made for expedience of testing in topic branches.

In addition, recipes can optionally filter out of toolchains or profiles. This is described further below.

Adding new toolchain versions is simply a case of adding new lines to this file, assuming machine availability.

Associating new profiles against existing toolchain versions is simply a case of appending to the list for the relevant version.

Removing a toolchain line will stop all future builds occurring on that toolchain, so is a way of declaring such builds are no longer needed for product maintenance.

#### Toolchain Versions
To add a new tool chain version to the pipeline add new lines to the sections with a `toolchain-setup-` prefix.
Each line starts with the toolchain name (`vs2017`, `xcode13`, `gcc7`, etc.) and is followed a platform specific script or value.

For example, to add Xcode 14.0.1 for both Intel and Apple Silicon builds:
```
[toolchain-setup-mac]
xcode10 = /Applications/Xcode.app/Contents/Developer
xcode13 = /Applications/Xcode13.2.1.app/Contents/Developer
xcode14 = /Applications/Xcode14.0.1.app/Contents/Developer

[toolchain-setup-mac_arm]
xcode13 = /Applications/Xcode13.2.1.app/Contents/Developer
xcode14 = /Applications/Xcode14.0.1.app/Contents/Developer
```

Then go to each of the `toolchain-` sections and assign the desired profiles prefix to the new toolchain. (`vfx22`, `vfx23`, etc.)

#### Conan configuration branch per profile
Generally, library package builds will use the default branch from [the configuration repo](https://a_gitlab_url/libraries/conan/configuration).

If a branch of the configurations needs to be tested, then all uses of a profile prefix can be told to remap to that branch. This is achieved through the pipeline config element such as

```
[config-branch-for-profile]
vfx22 = some_fix_for_vfx22_profiles
```

which says for any builds using the profile prefix vfx22, use the branch `some_fix_for_vfx22_profiles`.

## Package variations
Generating build commands through `pipelinecli` can be thought of taking default values from the tool's command line, applying specific overrides per variation of the recipe's `config.yml`, and generating a matrix of builds to schedule. The contents of the `config.yml` for each package considered for CI is schema validated to minimise incorrect behaviour from bad input.

In a basic `config.yml` file, package builds invoked through `pipelinecli` build only their _default recipe option values_ for all platforms. However, many packages require at least some combination of options to be built to be consumed by products at Foundry, or a subset of platforms, or build types. For example, `shared=True` and `shared=False`.

Instead of building _all_ possible combinations of option values, which may result in combinatorial explosion and excessive build times, there is an optional feature of a package's `config.yml` that can describe all combinations (variations) required.

All variations are specified per-version of a package.

### Simple variant sets
Each variation corresponds to a unique `conan create` command with one or more `-o` flags to specify the variation sets.

#### Option variations
For example, this builds `shared=True` and `shared=False` variations of version 1.70.0 of the package:
```yaml
versions:
  "1.70.0":
    folder: "all"
    variants:
      options:
        - shared: False
        - shared: True
```
Each variation set can contain multiple options, e.g. ensures `python_version=3` for both library types:
```yaml
versions:
  "1.70.0":
    folder: "all"
    variants:
      options:
        - shared: False
          python_version: 3
        - shared: True
          python_version: 3
```

#### Platform variations
For example, the following package version only builds on Windows:
```yaml
versions:
  "3.81":
    folder: "3.81"
    variants:
      platforms:
        - win
```
Use `win`, `linux`, `mac`, `mac_arm` to identify platforms; omitting any of them will disable the build for that platform for the affected package.

#### Build type variations
Similary, the following package version only builds on Windows, in Release, and generates a static library:
```yaml
versions:
  "3.81":
    folder: "3.81"
    variants:
      options:
        - shared: False
      platforms:
        - win
      build_types:
        - Release
```
Use `Debug` and `Release` to identify build types.

#### Configuration
Additional optional configuration may be applied to all the variations in the set to further refine what will be built and how. For example:
```yaml
versions:
  "3.81":
    folder: "3.81"
    variants:
      options:
        - shared: False
      platforms:
        - win
      build_types:
        - Release
      config:
        build_timeout: 123
        conan_request_timeout: 99
        conan_config_branch: nuke_defaults
        pkgref_namespace: null # or thirdparty/testing, for example
        pkgref_name: myawesomepackage
```
Each key on the configuration is optional.
##### `build_timeout`
This is the number of minutes that the build steps in the CI job have until timeout occurs.
##### `conan_request_timeout`
This is the time in seconds that the `conan upload` has before it times out.
##### `conan_config_branch`
This is the branch of https://a_gitlab_url/libraries/conan/configuration to install to the Conan local cache in each CI job.
##### `pkgref_namespace`
This is the "namespace" of the desired package reference, meaning the `user/channel` part of `name/version@user/channel`.
* This may be `null` to indicate package references of the form `name/version` in recipe. You will need to use `name/version@` on Conan's command line interface though.
* This may be `user/channel` to indicate a specific intent for a package reference. While this is free-form text, Jenkins builds are limited on the scope of `user` and `channel`. See the CreatePackageVFX20 build parameters for the known values.
##### `pkgref_name`
This is the "name" of the desired package reference. The use cases of this are likely to be uncommon, but may be encountered when a recipe can be shared among different named packages. Without this, the recipe would need to be duplicated.
###### Requirements:
1) Remove the `name` attribute from the package recipe.
2) Update the test_package so that any references to the name, be it via option querying, or `cmake_paths` variable querying in CMake, is data driven. To query the name of the package being tested, use `next(iter(self.requires))` in the test_package recipe. For Conan 1.44.0 and above, you may use `self.tested_reference_str.split("/")[0]` instead.

#### Inclusion/exclusion from active toolchains/profiles
While the `.pipeline-config` file defines the active toolchain versions to build each package for, not all versions of a package may be relevant. For example, older versions of a package may not be needed to be rebuilt for new toolchains or profiles.

As child of `variants`, the following may be specified, each of which is a list of wildcard expressions.

##### `only_profiles`
When a recipe version is only applicable to certain profiles:
```yaml
versions:
  "1.2.5.3":
    folder: "all"
    variants:
      only_profiles:
        - vfx20
```

##### `excluded_profiles`
When a recipe version is to be excluded from certain profiles:
```yaml
versions:
  "1.2.5.3":
    folder: "all"
    variants:
      excluded_profiles:
        - vfx22
```
`only_profiles` and `excluded_profiles` are mutually exclusive.

##### `excluded_toolchains`
When a recipe version is to be excluded from certain toolchain versions (and thus all profiles associated with it):
```yaml
versions:
  "1.2.5.3":
    folder: "all"
    variants:
      excluded_toolchains:
        - gcc*
        - xcode*
```

### Named variant sets
For the simple variation sets above, all variations under a package version inherit the same traits. You can think of it simply as a number of different Conan option combinations.

For more generic use, such as when you need different combinations of Conan options per platform, or per build-type, say, use named variant sets. This is just another level in the variants mapping in the `config.yml`. An example:
```yaml
versions:
  "3.81":
    folder: "3.81"
    variants:
      first_variant:
        options:
          - feature: "A, B, C"
        platforms:
          - win
      second_variant:
        options:
          - feature: "D, E, F"
        platforms:
          - linux
```
This example specifies two variants, one for Windows, one for Linux, but with a different Conan option values for each platform. It is not possible to describe this in the simple variant sets.

The names of the variant sets have no impact on the generated code, but simply used as monikers, which you will see in the CI pipelines.

The contents of named variant sets must be unique.

All the features of the simple variant sets can be used in named variant sets.

#### Hidden named variant sets
Similar to hidden jobs in GitLab CI, one can specify a hidden named variant by starting with a period, and use it as a YAML anchor.

For example, two variants sharing a common set of options, but then applying different profile applications:
```yaml
versions:
  "3.81":
    folder: "3.81"
    variants:
      .common: &common
        options:
          - shared: True
      first_variant:
        <<: *common
        only_profiles:
          - vfx*
      second_variant:
        <<: *common
        only_profiles:
          - vfx20
```

## CMake error logs saved for retrospection
Should a build job fail, the GitLab pipeline has been configured to hive off artifacts matching the filename CMakeOutput.log and CMakeError.log. These are standard log files generated by CMake. These files are saved in the job artifacts as a convenience to diagnosing the error, and may be accessed through the GitLab web interface for the job to inspect or download. These files are only kept by GitLab for a limited time.

## Package build environments
**NOTE: This is now deprecated and will be removed in a future update of pipelinecli.**

A sibling configuration option alongside variations is to allow environment variables to be set for package versions, either for all platforms (global), or per platform. When these are combined, platform specific environment variables take precedence, so will override the values of keys that are set in both global and platform specific entries.

For example, consider these settings in a package's `config.yml`:
```yaml
versions:
  "2019_U6":
    folder: "all"
    env:
      global:
        MY_ENV: "foo"
        YOUR_ENV: "fu"
      mac:
        MY_ENV: "bar"
```
For all platforms, `MY_ENV=foo` except for Mac, which has `MY_ENV=bar`.

All platforms have `YOUR_ENV=fu`.

## Skipping CI
CI can be skipped either through individual commit messages (only when you push one commit at a time) or through push options (for Git clients >= 2.10). Please refer to the [official GitLab documentation](https://docs.gitlab.com/ee/ci/yaml/#skip-pipeline).

### Disabling CI entirely on a branch
If, for unforeseen reasons, pipelinecli does not work on your topic branch, the `.gitlab-ci.yml` file can be deleted _in that branch_. Please ensure that you make this deletion without any other changes in a commit, so that it can be easily undone in a rebase, before merging back to `master`.

