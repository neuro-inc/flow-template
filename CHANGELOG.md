[comment]: # (Please do not modify this file)
[comment]: # (Put your comments to changelog.d and it will be moved to changelog in next release)
[comment]: # (Clear the text on make release for canceling the release)

[comment]: # (towncrier release notes start)

Apolo Platform Flow Template v25.7.0 (2025-07-04)
===================================================


No significant changes.


Apolo Platform Flow Template v25.01.07 (2025-01-07)
===================================================


Features
--------


- This version includes changes to the workflow and project configuration files to enable code completion and validation by adding schema references to Apolo's config yaml files. These changes will improve the development experience by providing better code completion and validation.

  Changes:

  {{cookiecutter.flow_dir}}/.apolo/live.yml: Added schema reference for code completion support in the live workflow configuration file.
  {{cookiecutter.flow_dir}}/.apolo/project.yml: Added schema reference for code completion support in the project configuration file. ([#699](https://github.com/neuro-inc/flow-template/issues/699))

- This version includes changes to Dockerfile to the new runtime image

  Changes:

  {{cookiecutter.flow_dir}}/Dockerfile: Upgraded image to v24.12.0 ([#700](https://github.com/neuro-inc/flow-template/issues/700))


Misc
----

- Use ".apolo" directory instead of ".neuro" and apolo* files istead of neuro* to configure apolo-flow. ([#705](https://github.com/neuro-inc/flow-template/issues/705))


Apolo Platform Flow Template v24.11.12 (2024-11-26)
===================================================


Misc
--------


- Moved apolo-flow actions to a new organization. ([#698](https://github.com/neuro-inc/flow-template/pull/698))


Apolo Platform Flow Template v24.11.11 (2024-11-11)
===================================================


No significant changes.


Neuro Platform Flow Template v23.07.10 (2023-07-10)
===================================================


No significant changes.


Neuro Platform Project Template v22.12.07 (2022-12-07)
======================================================


No significant changes.


Neuro Platform Project Template v22.05.04 (2022-05-04)
======================================================


No significant changes.


Neuro Platform Project Template v22.04.26 (2022-04-26)
======================================================


Features
--------


- Added project owner and role generation in post-generate hooks. ([#596](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/596))

- Replace base image reference `neuromation/base:v1.8.1-runtime` -> `ghcr.io/neuro-inc/base:v22.2.1-runtime`. ([#566](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/566))

- Use full storage and image URIs in the template ([#590](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/590))


Neuro Platform Project Template v22.02.01 (2022-02-01)
======================================================


Features
--------


- Added data folder to .neuroignore. Having this, you will not upload data files during the image build. However, `neuro-flow upload data` will work. ([#524](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/524))

- Added Python `3.10` support, renamed image `myimage` to `train` for its verbosity, added optional project description. ([#537](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/537))


Bugfixes
--------


- Fix apt dependencies installation if the project template is used on Windows (CRLF instead of LF file endings). ([#540](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/540))


Deprecations and Removals
-------------------------


- Drop Python `3.6` support. ([#537](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/537))


Neuro Platform Project Template v21.10.22 (2021-10-22)
======================================================


Features
--------


- Added GitHub workflow, which will automatically bump Neuro-Flow action tags if they are hosted in the GitHub, referenced by the release tag, and a newer tag is available. ([#505](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/505))


Bugfixes
--------


- Do not duplicate folders in the created project directory. ([#517](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/517))


Neuro Platform Project Template v21.08.25 (2021-08-25)
======================================================


Features
--------


- Added syntax hints for Neuro Flow configuration files. ([#497](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/497))


Bugfixes
--------


- Removed hard-coded preset names from the project template. ([#498](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/498))


Neuro Platform Project Template v21.06.10 (2021-06-10)
======================================================

No significant changes.

Neuro Platform Project Template v21.04.12 (2021-04-12)
======================================================

Features
--------


- Pin neuro-actions' versions used in the template ([#458](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/458))


Neuro Platform Project Template v20.12.30 (2020-12-30)
======================================================

Bugfixes
--------


- Fix volumes mounting point references for train and multi-train jobs. ([#430](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/430))


Improved Documentation
----------------------


- Added towncrier for changelogs generation, changed versioning style to date-based. ([#431](https://github.com/neuro-inc/cookiecutter-neuro-project/issues/431))


### v1.8 (15-12-2020)
```
c160e5a Restore preset for jupyter
6366007 Remove invalid preset from jupyter action
d1f90d9 Update default preset
e7db9c5 Update default preset
e92f922 [docs] Update RELEASE.md
995f776 Update neuro-cli pypi package name (#429)
4bb156c Add the preset into args. (#428)
73ce733 Fix typo in live.yaml
65e21ba [docs] Update internal docs (#427)
866b8aa Migrate to external neuro-flow actions (#425)
6dd7045 Bump cryptography from 2.8 to 3.2 (#424)
448c2e7 [Template] Migrate template from makefile to neuro-flow (#419)
94e218b [Tests] Support new job status in tests (#418)
```

### v1.7.6 (28-08-2020)
```
618ea84 [Makefile] bump base_image to v1.7.6
f8cc2f6 [tests] Drop filebrowser test (#416)
61847d1 [tests] Rename the Makefile target "init" to "setup" (#409)
99addfa [tests] Delete tqdm test (#415)
400757f [tests] Drop W&B completely (#411)
79b4ff1 [tests] Fix tests (#410)
3b4814f [tests] Update tests
```

### v1.7 (30-07-2020)
```
890d690 [docs] Update docs (#408)
537f20e [Makefile] Remove hypertrain (#407)
644151d [Makefile] Secrets support (#400)
414053c Fix version
5dce8dd [Makefile] Bump base env version to v1.7 (#405)
8650a7a [tests] Drop flaky tests on W&B and hypertrain (#406)
84b3a06 [doc] Add release instructions (#404)
2b8a681 [Makefile, tests] Adapt Makefile to neuro>=20.6.23, Simplify tests (#398)
```

### v1.6.1 (17-06-2020)
```
e3d910b [Makefile] No upload-notebooks before each command (#396)
70ba4a3 Disable life-span for Jupyter job (#397)
```

### v1.6 (18-05-2020)
```
4b0b20b [Makefile] Stabilize W&B Hypertrain + Set up CI for MacOS (#390)
bd988f3 [Makefile] Sync directories optionally (#386)
099d601 [tests] Use tags instead of image names (#391)
31969f7 [tests] Switch tests on AWS (#392)
e60fb2b Minor improvements to simplify NNI integration (#389)
c0558a1 [Makefile] Bump base env version to v1.5
```
