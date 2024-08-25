Release Checklist
=================

Non-stable releases are made from `main`, stable releases from the stable branch.

Generic steps:

* Change version in `pyproject.toml`.
* Change version in `snr/version.py`.

Extra steps for a stable release:

* Update images to reflect the latest changes.
* Change version in `tools/get_stable.sh` to use the new version.
* Merge branch `main` into `stable`. There will be conflicts.
* On the conflicts, ensure the correct version (without `+git`), anything else force it.

To do the release itself:

* tag name: `v<VERSION>`. **Non-stable releases are made from main, stable releases from the stable branch.**
* title would be: `Snr v<VERSION>`
* The content would be taken from `CHANGELOG`.
