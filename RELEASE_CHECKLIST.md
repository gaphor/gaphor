Although we strive to make releases as automated as possible, there are a few steps that we need to take to release a new version.

- [ ] Ensure all of the PRs since the last release are labeled with chore, fix, feature, translation, or skip-changelog.
All of the items in the draft release should be under the Features, Bug Fixes, Maintenance, or Translation headings.
- [ ] Update gaphor/services/helpservice/about.ui with any additional contributors since the last release,
update the version number, and check the copyright year.
- [ ] Test the previous build packages in Windows and macOS to ensure they launch successfully.
- [ ] Bump the version by updating it in the `pyproject.toml` file or by running `poetry version X.X.X`.
- [ ] Bump the AppImage version by running `cd _packaging/appimage`, `make update VERSION=a.b.c`
- [ ] Go to the release, click on edit draft. Add a summary to the title in the draft release.
- [ ] In the draft release, update the version tag to the correct version (remove the v in front). Click on Publish Release.
- [ ] Wait for the build to finish and the release artifacts to be uploaded. The PyPI release is made automatically during
the build.
- [ ] In the https://github.com/flathub/org.gaphor.Gaphor repo, create a new branch. Run `make update VERSION=X.X.X`.
Commit your changes and create a PR.
- [ ] Wait for the build to finish, install the test build using the instructions, and ensure that it launches using
`flatpak run org.gaphor.Gaphor`.
- [ ] Merge the PR.
- [ ] In the https://github.com/gaphor/gaphor.github.io repo, edit the `_config.yml` file and set the `gaphor_version` to the
updated version.
- [ ] Join the #thisweek:gnome.org Matrix room and write to the TWIG-Bot about the new version.
- [ ] Announce the new version on Twitter. :tada:
