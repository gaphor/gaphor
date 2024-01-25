Although we strive to make releases as automated as possible, there are a few steps that we need to take to release a new version.

- [ ] Ensure all the PRs since the last release are labeled with chore, fix, feature, translation, documentation, or skip-changelog.
All the items in the draft release should be under the Features, Bug Fixes, Maintenance, or Translation headings.
- [ ] Update `gaphor/ui/help/about.ui` with any additional contributors since the last release.
- [ ] Test the previous build packages in Windows and macOS to ensure they launch successfully.
- [ ] Bump the version by updating it in the `pyproject.toml` file or by running `poetry version a.b.c`.
- [ ] Go to the release, click on edit draft. Add a summary to the title in the draft release.
- [ ] In the draft release, update the version tag to the correct version. Click on Publish Release.
- [ ] Wait for the build to finish and the release artifacts to be uploaded.
      The PyPI release is made automatically during the build.
      Pull requests are created for https://github.com/gaphor/gaphor.github.io and https://github.com/flathub/org.gaphor.Gaphor.
- [ ] In the https://github.com/flathub/org.gaphor.Gaphor repo, install the test build using the instructions, and ensure that it launches using `flatpak run org.gaphor.Gaphor`. Then merge the PR.
- [ ] In the https://github.com/gaphor/gaphor.github.io repo, verify and merge the pull request.
- [ ] Join the #thisweek:gnome.org Matrix room and write to the TWIG-Bot about the new version.
- [ ] Announce the new version on Mastodon. :tada:
