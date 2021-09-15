# ASWF Continuous Integration Working Group

The ASWF’s investment in CI build infrastructure will provide the industry’s open source software community with the solid foundation needed to improve best practices and address the unique challenges we face.

The benefits to the community of having a CI build infrastructure include:

* Sharing open source build configurations, scripts, and recipes enables reference builds and alignment between user and vendor configurations
* Reduce duplicated effort in creating build and runtime environments to run open source software, extending VFX Reference Platform adoption with benefits to open build configurations and reference builds
* Facilitate community development by exposing the tools necessary to build, run and test OSS
* Reference builds are produced outside one organization’s firewall and the organization is not in the distribution path
* Lower the barrier to entry for using additional software components and software development
* Increased adoption of the VFX Reference Platform

Goals of the CI WG are:

1. Managing multiple version builds, plus requirements for dependencies via the VFX Reference Platform
2. Consultative assistance transitioning to a community CI platform
3. Support for Mac and Windows builds in addition to Linux
4. Support for GPU-enabled build and testing
5. Support for integration of commercial applications and libraries for testing purposes
6. Help integrate ASWF projects with established package management systems

Non-goals of the CI WG are:

1. The CI Working Group does not aim to prescribe to individual projects how they should set up their infrastructure: projects are free to adopt or adapt what best suits their needs.

The TAC member sponsor of this working group is Daniel Heckenberg.

## Deliverables

Docker configurations for VFX Reference Platform guided dependencies on [GitHub](https://github.com/AcademySoftwareFoundation/aswf-docker)

Docker container images providing VFX Reference Platform compliant build environments hosted from an [unthrottled Docker Hub account](https://hub.docker.com/u/aswf)

Sample project, including CI configuration on [GitHub](https://github.com/AcademySoftwareFoundation/aswf-sample-project)

Active CI for all ASWF projects using a common platform, GitHub Actions.

GPU accelerated builders to run project tests which require a GPU.

[JFrog Repository instance](https://linuxfoundation.jfrog.io/artifactory/aswf-conan/) to host build artifacts for ASWF projects.

Signing infrastructure for releases and build artifacts.

## Communication

The ASWF CI WG communicates on the following channels:

* [ASWF TAC mailing list](https://lists.aswf.io/g/tac)
* [ASWF Slack #wg-ci channel](https://academysoftwarefdn.slack.com/archives/C0169RX7MMK)

## Meetings

See the [ASWF public calendar](https://lists.aswf.io/calendar). This WG meets once every 4 weeks on off weeks from the biweekly TAC meeting, 13:00-14:00 Pacific Time.

[Video Conference Link](https://zoom.us/j/757849640?pwd=QzE1K2hrL2FHSFhKK3h5Z3BWTFJsZz09)

## Meeting notes

Meeting notes, recordings, and any presentations made during WG meetings are available [here](meetings).
