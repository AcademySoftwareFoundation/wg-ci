# Policies: At a glance

## Common
For all recipes:

* Use Python 3(.7) syntax
* Use topic branches to develop, and a rebase workflow to provide a clean history to fast-forward merge after review
* Ensure the `license` recipe attribute selection is correct from [SPDX](https://spdx.org/licenses/) or our [custom license repository](https://a_gitlab_url/libraries/conan/spdx-licences-proprietary)
* [`exports_sources`](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#exports-sources) recipe attribute values should be *just* those needed to make `conan create` work - do not use `*`
* Specify the recipe attribute [`revision_mode=scm`](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#revision-mode) to map Artifactory to GitLab
* Specify the recipe attribute `package_originator = 'External'` for thirdparty libraries
* Specify the recipe attribute `package_exportable = True` for open source libraries or `package_exportable = False` for closed source libraries
* Keep build scripts decoupled from Conan
  * Use the `cmake_paths` generator to teach CMake where Conan packages reside in your local cache
* For production builds, ensure the source tree referenced for a library is a mirror on Foundry's GitLab server
  * Ask DevOps to create new mirrors when needed
* Provide a `test_package` alongside the library recipe to exercise the generated package
  * For built libraries, test an API that requires linkage
* Use variants in `config.yml` files per package to describe each variant of the package needed to be built to satisfy all consumers
* For experimental recipes, these do not need to be reviewed by merge request (MR), but ***do not*** use the production namespaces for package references
* For production-ready recipes, a successful merge request will automatically spawn a GitLab CI pipeline to build the changed packages and upload to the production remote on Artifactory

## New recipes
Specifically for those recipes that did *not* previously exist in this repository:

* Specify `name` and `version` recipe attributes in *lower case alphanumerics*
  * Versions will be in `conandata.yml` and `config.yml` files if omitted from the recipe
* Omit `user` and `channel` from built package references specifying a `null` value for a [`pkgref_namespace`](ci.md#pkgref_namespace) in `config.yml` variants

## Recipes in maintenance
Specifically for those recipes that *did* already exist in this repository:

* Use `thirdparty` as the `user` and `development` as the `channel` for production quality builds
  * This is the default in GitLab CI
