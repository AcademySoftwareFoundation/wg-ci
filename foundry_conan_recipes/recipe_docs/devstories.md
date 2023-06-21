# Developer stories

> **_Note_**: the following covers workflows for Thirdparty packages. There may be changes made to accomodate Foundry packages in the future.

The following stories assume you have:
* familiarity with [Git](https://git-scm.com/), and preferrably [GitLab](https://about.gitlab.com/) methodologies,
* some familiarity with [Conan](https://conan.io/) command line invocation,
* a Git clone of `git@a_gitlab_url:libraries/conan/recipes.git` to work in,
* Conan installed in your Python environment (version 1.28.1 currently)

For the purposes of illustration, we will consider a package named `foobar` at version `1.2.3`.

<!-- using MarkDown All In One extension in VSCode for the TOC -->
- [Developer stories](#developer-stories)
  - [Intended Git usage](#intended-git-usage)
    - [Branch semantics of the recipes repository](#branch-semantics-of-the-recipes-repository)
    - [Rebasing](#rebasing)
    - [Squashing on a topic branch](#squashing-on-a-topic-branch)
    - [Partitioned `master` history](#partitioned-master-history)
    - [Patching preferences](#patching-preferences)
  - [How to set up your Conan local cache](#how-to-set-up-your-conan-local-cache)
  - [How to start writing a new package](#how-to-start-writing-a-new-package)
  - [How to create a package to experiment with](#how-to-create-a-package-to-experiment-with)
  - [How to convert an experimental package to production quality](#how-to-convert-an-experimental-package-to-production-quality)
  - [How do I know I need a GitLab mirror?](#how-do-i-know-i-need-a-gitlab-mirror)
  - [How to ensure your recipe adheres to license compliance](#how-to-ensure-your-recipe-adheres-to-license-compliance)
  - [How to use proprietary thirdparty licenses](#how-to-use-proprietary-thirdparty-licenses)
  - [How to ensure recipes are properly licensed for multi-library packages](#how-to-ensure-recipes-are-properly-licensed-for-multi-library-packages)
  - [How to add a feature or bug fix an existing recipe](#how-to-add-a-feature-or-bug-fix-an-existing-recipe)
  - [How to choose the naming of a package reference](#how-to-choose-the-naming-of-a-package-reference)
  - [How to teach Conan to fetch the package's source code](#how-to-teach-conan-to-fetch-the-packages-source-code)
  - [How to merge your working branch back to `master`](#how-to-merge-your-working-branch-back-to-master)
  - [How to modify the source code built by a recipe](#how-to-modify-the-source-code-built-by-a-recipe)
  - [How to build your package](#how-to-build-your-package)
  - [How to build your package in different profiles](#how-to-build-your-package-in-different-profiles)
  - [How to get your package builds onto Artifactory for everyone to use](#how-to-get-your-package-builds-onto-artifactory-for-everyone-to-use)
  - [How to get your package builds onto Artifactory for everyone to use (Obsolete Jenkins mechanism)](#how-to-get-your-package-builds-onto-artifactory-for-everyone-to-use-obsolete-jenkins-mechanism)
  - [How to avoid coupling CMake to Conan](#how-to-avoid-coupling-cmake-to-conan)
  - [How to associate commits/merge requests to Target Process](#how-to-associate-commitsmerge-requests-to-target-process)
  - [How to use a GUI front end to Conan](#how-to-use-a-gui-front-end-to-conan)
  - [How to use package binaries built using older compiler toolchains without recompiling them](#how-to-use-package-binaries-built-using-older-compiler-toolchains-without-recompiling-them)
    - [When cheats go wrong](#when-cheats-go-wrong)
  - [How a typical recipe review works](#how-a-typical-recipe-review-works)
  - [How I can add binary files next to my recipe](#how-i-can-add-binary-files-next-to-my-recipe)
  - [How to interpret the different hashes involved in a Conan package reference](#how-to-interpret-the-different-hashes-involved-in-a-conan-package-reference)
    - [Recipe revision](#recipe-revision)
    - [Package id](#package-id)
    - [Package revision](#package-revision)
  - [How can I pin a package reference to an older revision?](#how-can-i-pin-a-package-reference-to-an-older-revision)
  - [How do I know how much to rebuild when I've changed a recipe](#how-do-i-know-how-much-to-rebuild-when-ive-changed-a-recipe)
  - [How I can add more configurations to an existing package (obsolete)](#how-i-can-add-more-configurations-to-an-existing-package-obsolete)
  - [How useful are the user and channel parts of a package reference anyway](#how-useful-are-the-user-and-channel-parts-of-a-package-reference-anyway)
  - [How I work through Conan erroring with 'Can't find a package'](#how-i-work-through-conan-erroring-with-cant-find-a-package)

## Intended Git usage
See the #git Slack channel for lots of discussion on Git usage.

### Branch semantics of the recipes repository
The `master` branch is considered the 'truth' for production quality Conan recipes.

The `master` branch is [protected](https://docs.gitlab.com/ee/user/project/protected_branches.html), meaning that only designated people can push to it. Do not commit directly to `master`.

Instead, every non-`master` branch is where new recipes are developed, features are added, and bugs are fixed. These are known as [topic branches](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows). These are subsequently reviewed in a merge request, and merged to the `master` branch. These branches can also be very short lived, and never merged, for example, to do testing of the GitLab based CI.

All recipes reside in the one repository, so when you branch, you get everything. This is modelled similarly to the public [conan center](https://github.com/conan-io/conan-center-index) repository.

### Rebasing
In topic branches, you are free to work, but also required to keep up-to-date with `master`. In order to keep a linear history, and also your topic branch's changes ahead of `master`'s, it is required to using a rebasing methodology. Thus, in order to catch your branch up with `master`, you would do
```bash
git fetch
git rebase origin/master
```
This may result in conflicts, which you should fix before continuing with the rebase.

You can ensure that your changes are ahead of the latest `master` changes using:
```bash
git log --oneline --graph
```

This is most important when your merge request is close to being merged, as we'll want just your new commits to be slotted in on top of `master` when it merges.

### Squashing on a topic branch
As part of a rebase workflow on topic branches, you may want to squash your commits. For example, while you are prototyping in a topic branch, perhaps you added something which you no longer need, so squashing would remove it from history before it ends up in `master`. While this is encouraged to have a clean history, there are times that are more suitable for squashing than others.

After a merge request has been opened, I would not recommend squashing until the review is nearly complete. The reason for this is that squashing tends to confuse the sequence of comments on code, and GitLab cannot track when changes have been made regarding a comment. So it is a little harder to track for a reviewer.

Always retest after squashing and before force pushing to ensure that something hasn't gone awry.

Never trust auto-squashing on merge; always do it manually, so that the SHAs are honoured, comments are structured as you want them to be.

### Partitioned `master` history
If you look at the graph history of `master` with `git log --oneline --graph` then you'll see it snakes along between merge points. Each merge point is when a topic branch was merged back in, and the topic branch is listed in the merge point. However, the merge point is just for identification. The commits below the merge point are all those commits from your topic branch, and will be the same SHA as was in your topic branch (they were fast forwarded). This enforces the importance of a rebasing methodology, to have a clean history, but such that it is still identifiable by which topic branch changes were introduced from. It tells a story of a team of developers.

If you don't want to see the merge points, you can use `git log --oneline --graph --no-merges`, to see the fully linear history.

### Patching preferences
The preference for all patches, code and build script, is to make a commit to the library's mirror in GitLab. Ideally, of course, we'd like our recipes to build library code out of the box; in this case, we can track the SHA for versioned tags in library mirrors. When we do have to make changes, a `foundry/vX.Y.Z` branch is made from the `X.Y.Z` tag, and commits applied on that branch. Recipes then track a SHA in that branch, usually that referencing the HEAD of the branch.

## How to set up your Conan local cache
Conan uses a [local cache](https://docs.conan.io/en/latest/mastering/custom_cache.html) to define its behaviour, share common settings between users, and store local copies of package binary builds.

You can use your default Conan local cache, in your home directory, or you can define the locations of your own local caches (of which there can be many), using environment variables to change the behaviour of the Conan CLI commands. See [CONAN_USER_HOME](https://docs.conan.io/en/latest/reference/env_vars.html#conan-user-home) for all platforms and [CONAN_USER_HOME_SHORT](https://docs.conan.io/en/latest/reference/env_vars.html#conan-user-home-short) additionally for Windows.

Foundry usage requires a local cache to be configured in a certain way, and for profiles to be installed into it. These profiles are predefined groups of settings and options that define common build configurations at Foundry. We define these for the [VFX reference specifications](https://vfxplatform.com/), for each platform, for Debug and Release.

Local caches can be configured (at any time) using
```bash
conan config install git@a_gitlab_url:libraries/conan/configuration.git
```
first ensuring to set the appropriate environment variables to select the intended local cache.

Note your product may require you to use a specific branch of the configuration Git repository. See product local documentation for requirements.

## How to start writing a new package
> All new recipes must use lowercase alphanumerics for `name` and `version`.

This assumes recipe creation from scratch, rather than cloning an existing recipe, which is more along the lines of maintenance steps.

These notes are applicable whether you plan on making a production recipe or just one to experiment with.

Ensure you have the latest recipe `master` branch code locally
```bash
git checkout master
git fetch origin
git rebase origin/master
```
Make a working branch, with a name that is appropriate to the purpose of the branch, e.g.
```bash
git checkout -b import_foobar
```
For naming, you may also consider namespacing the branch with your initials, if you want to keep branches made by yourself logically grouped, e.g.
```bash
git checkout -b mf/import_foobar
```
There are no current restrictions on use of case, although [snake_case](https://en.wikipedia.org/wiki/Snake_case) is prevalent in existing branches.

Create a directory to house your recipes.
```bash
mkdir -p thirdparty/foobar/all
```
The use of `all` as a subdirectory is dependent upon a number of things. We try to follow a version agnostic recipe methodology (seen in public Conan recipe repositories, such as [Conan Center](https://github.com/conan-io/conan-center-index)). `all` indicates that the recipe contained within it is applicable to all versions. If this were not true, for instance, if there were 1.x and 2.x families of releases that had significantly different build instructions/dependencies, then you could have subdirectories `thirdparty/foobar/1.x` and `thirdparty/foobar/2.x` for separate recipes.

The first file to create is a Foundry specific configuration file that controls the versions we want to build, and the build variants of each version. This file is read by the auto-build systems, but not by local invocations of Conan.
```bash
touch thirdparty/foobar/config.yml
```
Fill this with the minimum required setup:
```yaml
versions:
  "1.2.3":
    folder: "all"
```
which maps versions to the subdirectory containing the appropriate recipe files.

To create stub recipe files from Conan provided templates, run:
```bash
cd thirdparty/foobar/all
conan new -t foobar/1.2.3
```
Note that `foobar` in `foobar/1.2.3` is initially set as the `name` attribute in the resulting `conanfile.py` (but can be modified). This attribute is used as part of the identity of the package when it is created, when it resides in your local cache, when it is uploaded to Artifactory, and when you refer to it as a dependent from other recipes. Due to there being case insensitive filesystems in Foundry's ecosystem, if a previous incarnation of the package exists, the name chosen should use consistent casing with what was used previously, otherwise there can be collisions in Conan/local caches.

The `-t` flag indicates creation of a `test_package` subdirectory and associated files. This is a required part of Foundry's recipe writing. Think of the test package as an integration test for consuming the files, generated by Conan from package creation that were put into the Conan local cache.
The `1.2.3` part of the command is redundant in this command for version agnostic recipes, but currently necessary by Conan CLI. To make the recipe version agnostic, open `conanfile.py` in an editor and remove the `version` attribute from the class:
```python
class FoobarConan(ConanFile):
  name = "foobar"
  version = "1.2.3" # remove this line
  ⋮
```

A file missing from this stub recipe, but necessary for Foundry usage, resides beside the generated `conanfile.py`, and is a built-in feature of Conan for data driven source selection per version:
```bash
touch thirdparty/foobar/all/conandata.yml
```
Fill this with the minimum required setup:
```yaml
sources:
  "1.2.3":
    git_url: <Git repository remote for foobar>
    git_hash: <some SHA in the remote>  # a useful comment about what this SHA refers to
```
This file is consumed by the Conan recipe beside it, and used in the `source()` method of the recipe to clone the source tree of foobar for the given version.

Build tool versions are globally defined in `requirements.txt` in the root of the recipes repository. Should a recipe require something different or additional, specify these in a recipe-local requiresments in `thirdparty/foobar/requirements.txt`.

While recipes are being developed, the `git_url` element is fine to be an external source. However, to get through review, this must refer to an internal GitLab repository. We mirror every thirdparty source tree in GitLab, and have foundry branches if we need to patch. Request a mirror, and/or versions you need, by asking DevOps. Also see [How do I know I need a GitLab mirror?](#how-do-i-know-i-need-a-gitlab-mirror) section.

GitLab allows [cross-project and cross-type references](https://about.gitlab.com/blog/2016/03/08/gitlab-tutorial-its-all-connected/), so if you need to refer to merge requests for source code and merge requests for recipes, or issues in either project, there is markup available for it.

The `git_hash` is a fixed point in history, so a SHA hash. Although the system will accept named references in Git, such as branch names and tags, it was decided to use hashes as immutable moments in history, and thirdparty package builds need to use fixed source in production.

It is now over to you to modify the template files to the Foundry standards (see [Confluence](https://a_wiki_url/wiki/spaces/DO/pages/1492549654/Conan+System+Guidelines) documentation), and to write the specific build steps for `foobar`.

Commit as often as you need to your branch. You have unrestricted usage in non-`master` branches. It is recommended to rebase against `master` as often as you feel comfortable. There may be changes in `master` that will improve the continuous integration, or documentation, or dependent recipes that you may want to inspect, and it is beneficial to be up-to-date. You will need to be fully up-to-date before merging.

When you are happy to push for the first time, run the command
```bash
git push -u origin import_foobar
```
The `-u` to connect to the new upstream branch.

Note that each push to the working branch will start a GitLab CI pipeline. This can be skipped. See [CI docs](ci.md) for more details.

Iterate over recipe updates until your package builds are successful in all required configurations.

## How to create a package to experiment with
The long term goal of the `master` branch of this repository is to contain all the recipes *used in production* by products. We can make use of features of Git and GitLab to support experiments and proofs of concepts, without the overhead of production quality.

First of all, follow the advice in [How to start writing a new package](#how-to-start-writing-a-new-package). This will give you a topic branch in the repository containing your experimental recipe(s).

The immediate benefit of being a topic branch here is that you can take advantage of the continuous integration system that applies to all topic branches, so you have confidence that your packages build on applicable platforms, in the desired variants.

If this is just an experiment, you **do not need to open a merge request**. That process is just for production quality packages.

In terms of sharing these experimental packages, currently you still need to head into Jenkins to do this, as described in [How to get your package builds onto Artifactory for everyone to use](#how-to-get-your-package-builds-onto-artifactory-for-everyone-to-use). The important aspect to note is that for experiments, you ***must not build into the production namespace used by packages***.

There are various other namespaces for package references, specified by the `user` and `channel` components of the reference. Implying a non-production context is one use for these. See [How useful are the user and channel parts of a package reference anyway](#how-useful-are-the-user-and-channel-parts-of-a-package-reference-anyway).

If you are creating a new recipe, then there will be no conflicts of interest in the non-production namespace you choose.

However if you are modifying an existing recipe for an experiment, be sure to first check if anyone else in Foundry is making use of that namespace on that package. Builds you make into that namespace will, by default, automatically get used by any other consumers, and this may surprise them.

If, at the end of the experiment, the recipe is not needed, the topic branch can simply be deleted. There will currently be artifacts left on Artifactory, but that is the current tradeoff of using this system and Jenkins to build the packages for Artifactory. Alternative workflows are being considered.

## How to convert an experimental package to production quality
There are a number of ways to do this:
 1. do the work yourself, and raise the merge request for reviewers to ponder,
 2. request some work from build experts (talk to you lead if you need to do this)

The benefit of the first approach is that you have all the details in your head already, and the context in which the package is to be used.

The downside to the second approach is that someone else will have to go in blind to potentially modify the experiment to bring it up to production quality. If a request is made, explicit requirements and details of how to test, would benefit whoever takes the recipe over.

Please refer to [How a typical recipe review works](#how-a-typical-recipe-review-works) for an idea of how a reviewer may approach looking at a recipe that is intended for production.

## How do I know I need a GitLab mirror?
When you are in early development of a Conan recipe for a thirdparty, it is perfectly fine to use the external Git repository for it. This can be used to verify your recipe through GitLab CI.

The point at which you do need to switch away from an external Git repository is either:
 1. you need to modify the repository, or
 2. you feel your recipe is complete enough for a review.

While 1) could be managed with personal forks in external Git providers, since this work is for Foundry, better to have an internal mirror and work on a branch.

If you are able to provide a test in the test_package that fails on the vanilla source code, but is fixed by a required modification to the source, then this is great for spotting regressions in library version upgrades.

DevOps have the ability to create new library mirrors in our GitLab server, and have scripts to automate this from external repositories. You need to provide the URL of the external repository, and the tag(s) of interest, since they can be the base of branches with necessary patches. We apply the patches to branches named `foundry/vX.Y.Z` where `vX.Y.Z` is usually the name of the tag of the version of interest to build. It is rare that we take builds from un-tagged SHAs, for the sake of stability and that others have tested a tag.

Contact DevOps either via the Conan package dev Slack channel, or by email through devops-requests.

## How to ensure your recipe adheres to license compliance
The license covering thirdparty code is very important, and is audited regularly. We are obliged to use non-viral/non-copyleft [FOSS](https://en.wikipedia.org/wiki/Free_and_open-source_software), paid-for proprietary licensed code, or own own licenses, in our products. Any sign of copyleft licenses, GPL mostly, is to be questioned if used by, or distributed with, our products.

Conan's recipes contain an attribute called [`license`](https://docs.conan.io/en/1.36/reference/conanfile/attributes.html#license) which accepts a short string identifier. As suggested in that link, we use the [SPDX](https://spdx.org/licenses/) site for the identifiers. For proprietary and Foundry defined licenses, we use a similar system, whereby an identifier is provided.

For FOSS licenses, use the SPDX listing to get the short identifier. For other licenses see [How to use proprietary thirdparty licenses](#how-to-use-proprietary-thirdparty-licenses).

License checks form part of the GitLab package CI system, and will fail the build if your recipe does not have an identifiable license identifier.

Finding the license for a thirdparty library is, in the case of FOSS, usually defined in a LICENSE or COPYING file in the root of their remote repository. You may also find it at the bottom of their README. It may also be in a comment section at the top of their source and headers.

When the license information is not in an obvious place, you may have to dig deeper, or ask your lead.

In any case of doubt, check with your lead. Additional information for your lead can be referenced from the [License section](../README.md#License) in the `README.md`.

To ensure that future maintainers don't miss details that may be buried deep in Git history, Conan test packages, where appropriate, should enforce any license compliance by testing aspects of the library.

## How to use proprietary thirdparty licenses
You may have come to this because the GitLab CI pipeline has failed for your recipe, indicating an invalid license.

When a new proprietary, or previously unknown FOSS, license (e.g. one that does not have an existing SPDX license identifier) is required, it can be added to the proprietary license repository.

To do this, clone the license repository:
```
git clone git@a_gitlab_url:libraries/conan/spdx-licences-proprietary.git
```

and make a new topic branch:
```
git checkout -b <INITIALS>/<BRANCH_NAME>
```

Create a new `.xml` licence file, whose name (minus the extension) matches the new license you would like to use, in the `licenses` directory. Use one of the existing licenses as a template, as there is a specific XML structure. Ideally, provide the real license text into the `<text>` element. If this is not available at the time, this will need to be returned to; please raise an issue/TP ticket to complete it.

Commit and push to your branch.

In your topic branch for your WIP recipe, modify the `.pipeline-config` file in the root of the repository, so that it refers to the branch of the SPDX repository:
```ini
[spdx]
extra-licenses-repo-url = git@a_gitlab_url:libraries/conan/spdx-licences-proprietary.git
extra-licenses-repo-branch = master # change this to your topic branch!
```
This is a temporary change in your topic branch, to test the license.

You can now modify your recipe's `license` attribute to match the basename of the license file you added.

For example, if the new license added was `licenses/my-new-license.xml`, then the conan attribute should look like this:
```python
license = "my-new-license"
```

The [CI docs](ci.md) has more details on how to use development branches when referring to the spdx-licences-proprietary repo.

Pushing to your recipe topic branch will schedule a CI pipeline, and the CI scripts will validate the license.

If the validation is successful, you need to schedule a merge request for your topic branch in [the SPDX licenses prioprietary repository](https://a_gitlab_url/libraries/conan/spdx-licences-proprietary). Once this has been approved and merged into the `master` branch, you can rebase your recipes topic branch to _remove_ the commit updating the `.pipeline-config` file that was temporary for testing. Pushing this will again schedule a CI pipeline, and will now validate your license against the `master` branch of the licenses repository.

## How to ensure recipes are properly licensed for multi-library packages
Some packages have multiple libraries. Take Qt for example. In such cases, be extra wary of licensing, as it may very per library. Take Qt, for example. The open source license for Qt actually varies per library, and while we dynamically link, meaning we can use LPGL (copyright), a few libraries are GPL only (copyleft) and must be excluded. See https://www.qt.io/product/features#js-6-3 for example.

Other thirdparty libraries may rely on system knowledge of licensing, such as Python, which on \*nix, comes with a `readline` module in the standard distribution. However, [readline is GPL](https://en.wikipedia.org/wiki/GNU_Readline) so we explicitly remove it from our Python package to be safe. This is an example that is explicitly checked for in the [test_package integration test](https://a_gitlab_url/libraries/conan/recipes/-/blob/master/thirdparty/Python/all/test_package/check_no_gpl_readline.py).

## How to add a feature or bug fix an existing recipe
Ensure that your local recipe `master` branch is up-to-date.
```bash
git checkout master
git fetch origin
git rebase origin/master
```
Create a new working branch with a suitable name for the change:
```bash
git checkout -b mf/fix_something_on_foobar
```
Commit your changes to your working branch.

When you are happy with changes, push to the remote
```bash
git push -u origin mf/fix_something_on_foobar
```

Pushing to the remote will execute the GitLab CI for the branch so that it checks package creation for all specified variants in the `config.yml`.

Iterate over recipe updates until your package builds are successful in all required configurations.

## How to choose the naming of a package reference
A package reference (in its simplest form) looks like
```
name/version@[user/channel]
```
where
* name - name of the package, as per the conanfile.py attribute
* version - version of the package
* user - user namespace (optional, but if used must be specified with channel)
* channel - channel of the namespace (optional, but if used must be specified with user)

For example:
```
boost/1.70.0@thirdparty/development
MiniCore/3.2.1@common/development
gRPC/1.43.0@
```

There are guidelines in the [Confluence](https://a_wiki_url/wiki/spaces/DO/pages/1492549654/Conan+System+Guidelines) documentation for what to use for user and channel.

> New thirdparty recipes should use an *empty* namespace for building packages into *production*, i.e. `name/version@`, which can be set in the `config.yml` using the [`pkgref_namespace: null`](./ci.md#pkgref_namespace) config.

> Existing thirdparty packages must use `@thirdparty/development` for *production* to avoid causing downstream recipe changes.

> Other namespaces can be used to indicate a fork, or testing, e.g. `@thirdparty/testing`, `@thirdparty/staging`.

There are other options too, but currently limited by the dropdowns available in the Jenkins build form. See the link above for the options. The one requirement is that you must check first if anyone else is using the chosen namespace, as you do not want to trample their usage.

## How to teach Conan to fetch the package's source code
In your package's recipe, you need a pattern similar to
```python
@property
def _source_subfolder(self):
    return '{}_src'.format(self.name)

def source(self):
    version_data = self.conan_data['sources'][self.version]
    git = tools.Git(folder=self._source_subfolder)
    git.clone(version_data['git_url'])
    git.checkout(version_data['git_hash'])
```
The Conan  `source` command is not expected to be run multiple times for thirdparty packages (and the above will error if your source directory exists). If any modification of code is required, a Git workflow such as that described in [How to modify the source code built by a recipe](#how-to-modify-the-source-code-built-by-a-recipe) should be followed.

The `_source_subfolder` property is to ensure in local workflow, using default parameters to Conan commands, that the source tree for your package is always in an untracked subdirectory, rather than in the same Git checkout as the recipe. Git then treats these as separate workspaces, such as in operations like `git clean`.

If you have a source tree that is made up of Git submodules, you need a modification to the above:
```python
    git.checkout(version_data["git_hash"], submodule="recursive")
```

## How to merge your working branch back to `master`
This is only applicable if your recipe is intended for production.

There are three gates to enaging a review:

1. do the builds succeed in GitLab CI? (mandatory)
2. has your lead signed off on everything (as a reviewer), especially the license (mandatory)

You may also want to consider reviewing the commit history in your working branch at this point. Merges are fast forward merges into `master` (and preferred not to auto squash), so cleaning the history at this point may be a good idea. Think about history from the point of view of future maintainers of the recipe(s) being merged.

Once these are in place, you can create a [Merge Request/MR](https://a_gitlab_url/libraries/conan/recipes/-/merge_requests) in GitLab, to begin the process of merging from your working branch to `master`.

Add people who are relevant as approvers.

Iterate over review feedback and make updates. Check the gates again.

Once approval has been reached, one of the maintainers of the recipes repository will be able to merge to `master` (the MR indicates who can merge). Your working branch is automatically deleted after merge by default.

After merging back to `master`, GitLab CI will automatically launch a new pipeline to build all variants of your modified packages, and upload to the production remote on Artifactory. The rebuild step is currently necessary since the packages from the topic branch CI step are emphemeral and may no longer exist. All variants must be built and uploaded because the recipe files have changed, and a new recipe revision will be generated, which all unpinned references in consumer packages will then begin to use.

## How to modify the source code built by a recipe
In your recipe's `conandata.yml`, each version of the package has a related SHA into its source repository. Making changes to the source code requires a little Git branch management.

You will need a working branch for the recipe as described for making a bug fix to a recipe, and you will also need a working branch on the source code repository.

There will already be a `foundry/v1.2.3` branch in the source code repository (in which the current SHA resides), and you need to branch from this to make changes.
```bash
cd <source code folder for foobar>
git fetch
git checkout -t origin/foundry/v1.2.3
git checkout -b mf/make_foobar_code_fixes
```
Once changes have been made, and commit and push. Note that changes to this repository will have no effect on packages yet, as nothing refers to the new SHAs pushed.

When making changes to a thirdparty library source tree, it is preferrable to backport fixes from newer releases into the version of the library in use (we don't often track latest). With Git, in order to add suitable breadcrumbs to the history, you can use [`git cherry-pick -x`](https://git-scm.com/docs/git-cherry-pick/en) to indicate where patches came from. Of course, this only works for patches that can be accepted 'as is'. For all other patches, please provide sufficient information in the commit message for the change to help future maintainers.

Identify the most recent SHA in your source code working branch. Put that into the appropriate YAML entry in `foobar`'s `conandata.yml`. Commit and push that into your recipe's working branch. CI will now consume the new source code SHAs.

Iterate over CI/Jenkins/updates until satisfactory.

To complete, in order:
* Get approved reviews of the source code working branch, and merge this back to the `foundry/v1.2.3` branch (_not_ `master`). Remember, no changes to Artifactory packages occur yet, because nothing refers to the changes.
* Follow the documented procedure for merging recipe changes back to `master`.

## How to build your package
There are two mechanisms; use `conan create` or the [local workflow](https://docs.conan.io/en/latest/developing_packages/package_dev_flow.html). Either should be possible, so ensure to test both. Automated builds will use `conan create`.

While it is convenient to use `conan create` locally sometimes, it is worth noting that that command will repeat _every_ step of the package creation process on each run. While this can be streamlined by additional parameters, it is also not always efficient. Refer to the [Conan documentation](https://docs.conan.io/en/latest/reference/commands/creator/create.html) for more details. Also note that `conan create` operates entirely in your local cache.

A vanilla invocation of `conan create` is:
```bash
cd thirdparty/foobar/all
conan create -pr <profile> . 1.2.3@
```
meaning to build version 1.2.3 into an empty package reference namespace for the specified profile.

> Existing recipes must still use `@thirdparty/development` for their package reference namespace, while brand new recipes can use the empty namespace.

You do not need to specify the name of the package, as it is written in the recipe file (while the version (may, or may not be), and user and channel are definitely not specified).

An concrete example may be:
```bash
conan create -pr vfx20_linux_Release . 1.2.3@
```

The local workflow offers individual methods on recipes to be executed, and repeated, so is a much finer granularity than the monolithic create. The majority of the steps in local workflow occur _local_ to your recipe.
To duplicate what `conan create` does, you would do
```bash
cd thirdparty/foobar/all
conan install -pr <profile> . 1.2.3@
conan source .
conan build .
conan package .
conan export-pkg -pf package . 1.2.3@
conan test -pr <profile> test_package foobar/1.2.3@
```
More often than not, `install` and `source` are executed once. `build` is then executed repeatedly while the recipe/source is developed. `package` confirms locally that your package structure is put together correctly. `export-pkg` is when you are ready to copy your package to your local cache. `test` is executed repeated while you develop your test package to exercise your packaged files. This last step may then require iterating back to `build` again.

There are various other flags you can specify to each individual command that allows more flexibility on usage, such as where to write files. See the [Conan command documentation](https://docs.conan.io/en/latest/reference/commands.html) for details of the arguments.

## How to build your package in different profiles
If you can use `conan create`, just use each command in turn with different profiles as these operate entirely within your local cache, e.g.
```bash
conan create -pr vfx20_linux_Debug   . 1.2.3@
conan create -pr vfx20_linux_Release . 1.2.3@
```

If you use local workflow, then remember that most package development output files are written local to your recipe, and thus will, by default, be overwritten for each profile used in commands. One important step to note is that after changing profile, always re-run `conan install`, specifying the new profile, as this writes a number of Conan metadata files, and fetches dependencies mapped to the profile to your local cache.

Check the [Conan command documentation](https://docs.conan.io/en/latest/reference/commands.html) for command line arguments such as
* `-if` for install folder
* `-sf` for source folder
* `-bf` for build folder
* `-pf` for package folder
* `-tbf` for test build folder

## How to get your package builds onto Artifactory for everyone to use
Once a merge request has been merged, a new GitLab CI pipeline is automatically launched, which builds all variants of the packages modified in your merged commits. This new pipeline uploads packages to the production remote on Artifactory.

## How to get your package builds onto Artifactory for everyone to use (Obsolete Jenkins mechanism)
Artifactory uploads are restricted to those autobuilds on canonical build machines. Currently this is controlled by Jenkins.

Note that package builds exist on Artifactory in various states of readyness. Some are for production, while some are just for testing. Ensure you are using the correct user and channel in the options below to indicate the desired context.

For thirdparty builds, log into Jenkins at https://a_jenkins_url/job/CreatePackageVFX20/ using your LDAP credentials, and click on the `Build With Parameter` menu option. This will present you with a form to fill in. Usual options to set are:
* _vcs_type_ = git
* _vcs_path_ = `git@a_gitlab_url:libraries/conan/recipes.git`
* _vcs_reference_ = Leave blank for `master`; branch name for HEAD of that branch; SHA for a specific SHA. For official builds, this should be the SHA that your recipe files were last changed at.
* _conan_recipe_dir_ = \*nix style path to the directory containing your conanfile.py, e.g. `thirdparty/foobar/all`
* _build_versions_ = Leave blank for all versions in the config.yml, or specify one or more versions separated by commas
* _vfx_platform_ = vfx20 (others are available) - used to select profiles
* check boxes for platform + config (e.g. _linux_release_) - leave checked all relevant configs
* _skip_conan_upload_ = False (this is the default, so if you're just trying out a build, and don't want to see the results on Artifactory, change this to True)
* _skip_user_channel_ = False (this is NOT the default; but must be False in order for package references generated to use _conan_user_ and _conan_channel_ below. Specifying True here will cause both user and channel to be not used.)
* _conan_user_ = thirdparty (see dropdown options)
* _conan_channel_ = development (see dropdown options)
* _conan_options_ = leave blank for defaults option values as specified in the recipe, otherwise as you would pass to `conan create`, e.g. `-o foobar:shared=False` to indicate a static library build of foobar.
* _conan_config_branch_ = `master` (unless local product needs dictate a different branch)

Click the Build button once happy.

If your build fails for whatever reason, you can easily repeat the build without needing to fill the form in again, by browsing to the previous job that was built, and choose "Rebuild" from the left hand menu.

You can also use this technique to _modify_ any parameters in the form to build a _different_ variant of the package.

## How to avoid coupling CMake to Conan
It is desirable to _not_ refer to Conan in CMakeLists.txt files. This makes the CMake scripts portable.

What we use the Conan [`cmake_paths`](https://docs.conan.io/en/latest/reference/generators/cmake_paths.html) generator, and a CMake definition from the Conan recipe:
```python
cmake = CMake(self)
cmake.definitions["CMAKE_PROJECT_foobar_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
```
This enables automatic [code injection](https://cmake.org/cmake/help/latest/variable/CMAKE_PROJECT_PROJECT-NAME_INCLUDE.html#variable:CMAKE_PROJECT_%3CPROJECT-NAME%3E_INCLUDE) into the CMakeLists.txt `project` statement. The requirement is that the project name must match, so the above examples assumes CMakeLists.txt contains `project(foobar ...)`.

The Conan generator will produce a file called `conan_paths.cmake`, when the `install` command for Conan is executed, into the install folder.

It will append paths of recipe dependencies from your local cache into [CMAKE_MODULE_PATH](https://cmake.org/cmake/help/latest/variable/CMAKE_MODULE_PATH.html) and [CMAKE_PREFIX_PATH](https://cmake.org/cmake/help/v3.0/variable/CMAKE_PREFIX_PATH.html). CMake will then use these in [`find_package`](https://cmake.org/cmake/help/latest/command/find_package.html) commands, thus using your local cache as parts of its search directories.

Note that YMMV with this, and may require some CMake cajouling in the cases where the expected package is not found. Per package CMake find scripts may offer solutions here (e.g. [Boost_DEBUG](https://cmake.org/cmake/help/latest/module/FindBoost.html)), and modern CMake versions offer [CMAKE_FIND_DEBUG_MODE](https://cmake.org/cmake/help/latest/variable/CMAKE_FIND_DEBUG_MODE.html).

## How to associate commits/merge requests to Target Process
At the time of writing, there is no automation for this. Please manually link to GitLab in your TargetProcess entities.

## How to use a GUI front end to Conan
This is beyond the scope of this document, but you are referred to [barb](https://github.com/TheFoundryVisionmongers/barb) if you'd like to try it.

## How to use package binaries built using older compiler toolchains without recompiling them
Conan records ABI compatibility in its package binary builds by encoding metadata from [settings](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#settings), [options](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#options) and [requirements](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#requires) that the package recipe declares as interesting, as a [package identifier](https://docs.conan.io/en/latest/creating_packages/define_abi_compatibility.html). In particular, settings may contain the compiler version. By default, all of this metadata must match when Conan tries to resolve dependencies. However, we can apply knowledge that Conan does not have, such as some compiler toolchains producing ABI compatible binaries. For example, VisualStudio 2015 through to 2019; Apple Clang 8 through 12; GCC 4.8 through 6 (and perhaps beyond) when GCC is compiled correctly for STL ABI changes as it is on CentOS.

Fortunately, Conan gives us a [backdoor](https://docs.conan.io/en/latest/reference/profiles.html#package-settings-and-env-vars) to add this expert knowledge into its algorithms. The most effective way, in that it's shared amongst all relevant users in a single step, is to add the necessary changes to a profile stored in a configuration.

For example, suppose you are building an application on Linux. Your profile will contain something like the following to describe the setting used for the native application build:
```
[settings]
os=Linux
os_build=Linux
arch=x86_64
arch_build=x86_64
compiler=gcc
compiler.version=6
compiler.libcxx=libstdc++
build_type=Release
```
which encodes GCC 6 into the build.

Suppose also your application wants to use a binary build of package P, which has not yet been updated for GCC 6, but a binary build already exists that used GCC 4.8, and all other settings/options/requirements are satisfied. Since we know that the different compiler ouputs are ABI compatible, we can inform Conan of this by adding snippets like that below to your profile in the `[settings]` section:
```
[settings]
⋮
P:compiler=gcc
P:compiler.version=4.8
```
Because you're changing a sub-section of compiler (the version) you must also specify its parent in the override as shown.

From then on, instead of Conan insisting that binary builds of P must match the application's profile (GCC 6), it will allow consumption of binaries from GCC 4.8.

Foundry's Conan configurations, including profiles, are kept in git@a_gitlab_url:libraries/conan/configuration.git.

Products that require profile overrides create a branch of the `master` branch, and apply their changes. The product devs will then use an extension to the command described in [How to set up your Conan local cache](#how-to-set-up-your-conan-local-cache) by specifying the appropriate branch name, e.g.
```bash
conan config install git@a_gitlab_url:libraries/conan/configuration.git -a "-b some_product_specific_branch"
```

Of course, YMMV if you try to do this with non-ABI compatible compiler versions.

### When cheats go wrong
The above is useful when you know exactly what you need to make a build work. However, especially with shared Conan local caches between products, that you may get unexpected results, e.g. packages not being found.

The first thing to look at is the initial output from either `conan create` or `conan install` which lists all the settings and options in the build. If the settings refer to a particular package, then it has been overridden in a profile most likely (could also be `-s` switch to the commands, but less likely). Is the override exactly what you expected it to be?

If the override is coming from the profile, then you have two choices:
1) the profiles are all wrong for my product - check which branch of the configuration repository you installed,
2) profiles are correct for my profile, but package X is wrong - time to update your profiles, and commit them back to the configuration repository. (Note that this is leading to where we'd like to get to eventually, with no overrides in any profile.)

Installing a new branch of the configuration repository is straightforward, just duplicate the command above, specifying the intended branch (or leaving for the default). **NOTE**: This overwrites your local cache settings and cannot be recovered - it will not affect the packages already installed by Conan though.

## How a typical recipe review works
Note that recipe merge requests are only necessary for recipes intended for production. The review system is absolutely necessary in order to maintain the high standard we are seeking to minimise ongoing maintenance, promoting reuse, and minimising effort to consume in products.

These are typical things that get looked for in a review of a recipe:

1) Is the MR targeting the right branch?
2) Is the recipe versioned or version agnostic? (Prefer the latter; if not, find out why.)
3) Check the license attribute in the recipe. Does it match up with what's reported in the thirdparty's source tree? Is it a license we can use? Does the MR description, or recipe, contain details of which manager signed off on the license choice?
4) Are all the other recipe attributes filled out? Nothing set to None or an empty string?
5) Is the revision_mode attribute set to scm?
6) Is this a header only library? If so, are there settings and options? If so, find out why.
7) If this has a buildable library, is there are least shared and fPIC options? Do their possible values make sense? fPIC can be missing if the library is shared=True only. There should always be at least one of these options to identify the build, unless there are exceptional circumstances (provided binaries from a vendor).
8) Are requirements/build requirements using old or new style Conan packages? (`@foundry/stable` vs `@thirdparty/development` or `@`.)
9)  Are there any requirements that should be platform specific, but not conditionally added?
10) Does the source() method use the standard conandata structure? If not, find out why.
11) On Windows, is the fPIC option (if provided) deleted in config_options?
12) Are any package options set in config_options? If so, move them to configure().
13) Does configure() have anything other than checks and setting option values?
14) How is build() implemented? Validate the imports at the top of the recipe to ensure there are no unused imports.
15) If build() uses CMake, and has dependencies, is the cmake_paths generator specified in the recipe attributes?
16) For static builds, are symbols hidden in the build step?
17) In the build() method, is there suitable logic to handle static and shared libraries if both are supported?
18) In the build() method, is any CMake configuration delegated to a helper method?
19) In the package() method, is it a simple install (using autotools or CMake)? If not, find out why.
20) In the package() method, are any CMake config files hand rolled? If so, is this because the build doesn't use CMake, or the CMake scripts from the library do not provide suitable/incorrect install/export functionality?
21) In the package_info() method, are suitable setting provided? (Less rigorous here, since we mostly use CMake integration, but it is occasionally used in non-CMake library-library dependency builds.)
22) Is there evidence that the conanfile.py has been linted? (mostly watching out for redundant code here)
23) In the sibling conandata.yml file, are all suitable versions, with GitLab URLs specified? If not, ensure the author requests a mirror into GitLab.
24) In the conandata.yml file, compare the SHAs provided against where the comment suggests they should be referring to. If they don't, ask the author to verify.
25) In the conandata.yml file, do the SHAs suggest there are outstanding topic branches to be merged in for the source code? Ask the author.
26) Does a test_package directory exist? If not, ask author to implement the integration test using CMake.
27) Does the test package find the package just built?
28) Does the test package use something in the library package that will confirm that it has been built correctly?
29) Does a config.yml exist above the package directory? If not, ask the author to create one.
30) Does the config.yml specify all versions expected from what is in the conandata.yml?
31) Does the config.yml specify all variations you'd expect from the options in the conanfile.py?
32) Is there proof that it builds for all applicable platforms and variations? Check the GitLab CI pipeline (tab in the review). These will also check whether all necessary recipe attributes have been provided.
33) Are there a sensible number of commits to be merged into `master`? Does it make sense to squash/reorder some commits to make the 'story' that a maintainer will read in the `master` branch as more understandable.

## How I can add binary files next to my recipe
The short answer is, if you can avoid doing so, please don't add them.

The original concept for the recipes repository was to be purely text based, and so it has been configured that way.

However, some files have ended up going in, particularly those to do with image format testing.

Given the configuration of the repository, Git may incorrectly interpret binary files with combinations of bytes that look like EOL characters. We have seen this happen already for TrueType .ttf files.

See the https://a_gitlab_url/libraries/conan/recipes/-/blob/master/.gitattributes file for the current configuration. Exceptions may need to be added to the file types here, but hopefully this can happen _before_ any instances are added to the repository.

## How to interpret the different hashes involved in a Conan package reference
Previously, the simplest form of the package reference was shown to be
```
name/version@user/channel
```
In it's fully explicit form, it is
```
name/version@user/channel#rrev:id#prev
```
where

* rrev is the recipe revision
* id is the package id
* prev is the package revision

Reading from left to right, the identification of the precise binary to identify becomes _more_ specific.

If you leave parts out (removing from the right), Conan will fill in with the most recent of each part left out. It is most common to not specify the additional parts after the channel. However, if you do, we refer to it as pinning.

### Recipe revision
This is an identifier for a revision of the recipe text file and associated files. The origin of the hash depends on the `revision_mode` attribute in the recipe. By default it will hash the contents of all recipe related files. However, we use the alternate form when it takes the value `scm` which is the SHA of the Git commit that last changed said files. That way, we have a 1-1 mapping between Artifactory and Git.

A recipe revision has as date associated with it too.

### Package id
The package id is the hash of the settings, options and (by default) major versions of all _runtime_ dependencies of the recipe. This is to identify a unique variation of build of the package.

### Package revision
The package revision is a hash of the contents of the files generated from the packaging step. This is likely to change if the source code changes, but nothing in the recipe, or the profile, changes during the build.

A package revision has a date associated with it too.

## How can I pin a package reference to an older revision?
Suppose there is a package of interest, `FooBar/1.2.3@thirdpary/development`. Suppose this has several recipe revisions (simplyfing SHAs in this example):
```
89AB
4567
0123
```
available on Artifactory. Specifying the package reference as-is as a requirement (or build requirement) in a Conan recipe means (when revisions are enabled in the local cache) that the most recent revision is selected (top-most in the list here).

Suppose now that a change to the recipe occurs, and is built and uploaded, so that the revisions available are now:
```
CDEF
89AB
4567
0123
```
But something went wrong! A bug is introduced, and the `CDEF` revision is bad, and it will take some time to fix.

We don't have a good workflow for deleting revisions from Artifactory, so as a temporary measure you can 'pin' a requirement (or build requirement) to an older recipe revision, by appending the revision after the package reference. For example, to choose the slightly older revision (89AB), you would write `FooBar/1.2.3@thirdpary/development#89AB` in your conan recipe.

## How do I know how much to rebuild when I've changed a recipe
It is important to know, based on the revision_mode choice we made (scm), and that Conan will always choose the latest revision, that if you change something in a recipe, and build again for upload to Artifactory, you must build _all_ variations of the package, so that all consumers will always find their variation.

The config.yml file in the package lists all the variations that need to be built. GitLab package CI automates reading this and spawning properly.

## How I can add more configurations to an existing package (obsolete)
*This is not supported in the pure GitLab CI workflow - only on Jenkins*

On the counter-side to [How do I know how much to rebuild when I've changed a recipe](#how-do-i-know-how-much-to-rebuild-when-ive-changed-a-recipe), there is also the case when you have _not_ changed the recipe, and yet need to add a configuration for a binary build that didn't exist when the recipe revision was first uploaded.

An example of when this might happen is if new compiler versions are introduced. The recipe may already be suitable for use.

In this case, it is _very_ important to get the SHA of the last change to the recipe. This will match the most recent revision in Artifactory. Please ensure that you double check this before progressing.

Once you have the SHA of the most recent revision, you can fill in the Jenkins CreatePackageVFX20 job template and use that SHA as the `vcs_revision`, and modify the test of the job parameters to generate the new configuration (e.g. through using a different vfxspec for instance).

Because the SHA matches the existing revision, additional `package_id`s are appended to the existing revision in Artifactory. The new `package_id`s become available for any consumer to select, and existing `package_id`s remain, so that existing consumers are also unaffected.

If the wrong SHA is accidentally used, then _all_ variations need to rebuilt, in order to satisfy all consumers.

Using the Jenkins Bridge again, will ensure that SHAs are automatically queried and variations are built. It is still recommended that the SHAs suggested are double checked against the most recent revision in Artifactory.

## How useful are the user and channel parts of a package reference anyway
> New recipes only can use empty namespaces for production

The Conan developers have admitted that user and channel were added in the early days of Artifactory when it didn't have multiple remotes, and long before revisions were a thing in Conan. They were for identifying different builds of a package. If you look on the public Conan Center repository, they are phasing out the user of user and channel, so packages are mostly now referred to just by name and version.

We are, however, still using them. This was the original design for vfx20, as per the Confluence documentation, to create a tiered system of development through testing and production. However, in practice, we've not used it like that, which is why we've got a lot of packages in Artifactory with @thirdparty/development when they are in production.

In practice, however, the user and channel do offer a forking mechanism in order to identify a very different branch of a package. Think of them as a namespace. There have been a few examples of this, mostly on the channel side, to indicate 'not quite ready', and one example I'm aware of (FoundryGL) to indicate a user change (since channel might be useful yet again under that user).

At some point in the future, the user and channel may be removed for production, and left optionally as the 'fork' identifier.

## How I work through Conan erroring with 'Can't find a package'
Here's an example of the sort of error you might see in Conan
```
ERROR: Missing binary: USD/20.08@thirdparty/development:e29b359b83ab70a415b3c3ef4d3e83400b964ff5
USD/20.08@thirdparty/development: WARN: Can't find a 'USD/20.08@thirdparty/development' package for the specified settings, options and dependencies:
- Settings: arch=x86_64, build_type=Debug, compiler=apple-clang, compiler.libcxx=libc++, compiler.version=10.0, os=Macos
- Options: fPIC=True, imaging=True, python_version=None, shared=True, tbb:fPIC=True, tbb:shared=True
- Dependencies: tbb/2019_U6@thirdparty/development
- Requirements: tbb/2019_U6
- Package ID: e29b359b83ab70a415b3c3ef4d3e83400b964ff5
ERROR: Missing prebuilt package for 'USD/20.08@thirdparty/development'
```
At first sight, it is daunting.

Herein lies a problem with some of the hashes, particularly the package_id, that Conan uses - you can't de-hash them into its components that created them.

What the error is saying is that given the settings, options, and runtime requirements as listed, generated a package_id of e29b359b83ab70a415b3c3ef4d3e83400b964ff5, but Artifactory did not have that package id. So there is a mismatch between what Conan is being asked to find, and what is present.

You should at least go to [Artifactory](https://an_artifactory_url/ui/repos/tree/General/Conan_Foundry) and look through the packages available to see if what you wanted is there.

There really could be a missing package on Artifactory, in which case the solution involves building the missing variants on GitLab CI, so a modification to the config.yml may be required for the package.

Perhaps you don't care that the package isn't on Artifactory (as you're just testing), then pass the `--build` flag to Conan to build it locally.

But, if you really think it ought to be there, and thus there's a misconfiguration somewhere, there are things to check:

* The settings come from the profile (`-pr` switch), and `-s` switches passed to Conan.
* The options come from your recipe, the configure() method in your recipe, the default options for dependencies, and any `-o` switches passed to Conan.
* The major version numbers of runtime dependencies come from your recipe's requires attribute and requirements method, and transitively from all of those too.
