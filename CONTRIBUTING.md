# Contributing

### We :heart: our Contributors! 

First off, thank you for considering contributing to Gaphor. It's people like
you that make Gaphor such a great modeling tool.

### Why a Guideline?

Following these guidelines helps to communicate that you respect the time of
the developers managing and developing this open source project. In return,
they should reciprocate that respect in addressing your issue, assessing
changes, and helping you finalize your pull requests.

### What we are Looking For 

Gaphor is an open source project and we love to receive contributions from our
community — you! There are many ways to contribute, from writing tutorials or
blog posts, improving the documentation, submitting bug reports and feature
requests or writing code which can be incorporated into Gaphor itself.

### What we are not Looking For

Please, don't use the issue tracker for support questions. Check whether the
your question can be answered on the
[Gaphor Gitter Channel](https://gitter.im/gaphor/Lobby).

# Ground Rules
### Responsibilities 

 * Ensure cross-platform compatibility for every change that's accepted.
 Windows, Mac, Debian & Ubuntu Linux.
 * Ensure that code that goes into core meets all requirements in this
 [PR Review Checklist](https://gist.github.com/audreyr/4feef90445b9680475f2).
 * Create issues for any major changes and enhancements that you wish to make.
 * Discuss things transparently and get community feedback.
 * Don't add any classes to the codebase unless absolutely needed. Err on the side of using
 functions.
 * Keep feature versions as small as possible, preferably one new feature per
 version.
 * Be welcoming to newcomers and encourage diverse new contributors from all
 backgrounds. See the
 [Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/).

# Your First Contribution

Unsure where to begin contributing to Gaphor? You can start by looking through
these `first-timers-only` and `up-for-grabs` issues:

 * [First-timers-only issues](https://github.com/gaphor/gaphor/issues?utf8=%E2%9C%93&q=is%3Aissue+is%3Aopen+label%3Afirst-timers-only) -
  issues which should only require a few lines of code, and a test or two.
 * [Up-for-grabs issues](https://github.com/gaphor/gaphor/issues?utf8=%E2%9C%93&q=is%3Aissue+is%3Aopen+label%3Aup-for-grabs) -
 issues which should be a bit more involved than `first-timers-only` issues.

### Is This Your First Open Source Contribution?

Working on your first Pull Request? You can learn how from this *free* series,
[How to Contribute to an Open Source Project on
GitHub](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github).

At this point, you're ready to make your changes! Feel free to ask for help;
everyone is a beginner at first :smile_cat:

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code
has changed, and that you need to update your branch so it's easier to merge.

# Getting Started

For something that is bigger than a one or two line fix:

1. Create your own fork of the code
2. Install all development dependencies using:
`$ poetry install`
`$ pre-commit install`
If you haven't used poetry before, just run `pip install poetry`, and then run the commands above, it will do the correct thing.
3. Add tests for your changes, run the tests with `pytest`.
4. Do the changes in your fork.
5. If you like the change and think the project could use it:
    * Be sure you have the pre-commit hook installed above, it will ensure that
    [Black](https://github.com/ambv/black) is automatically run on any changes for
    consistent code formatting.
    * [Sign](https://help.github.com/articles/signing-commits/) your commits.
    * Note the Gaphor Code of Conduct.
    * Create a pull request.


Small contributions such as fixing spelling errors, where the content is small
enough to not be considered intellectual property, can be submitted by a
contributor as a patch, without signing your commit.

As a rule of thumb, changes are obvious fixes if they do not introduce any new
functionality or creative thinking. As long as the change does not affect
functionality, some likely examples include the following:
* Spelling / grammar fixes
* Typo correction, white space and formatting changes
* Comment clean up
* Bug fixes that change default return values or error codes stored in constants
* Adding logging messages or debugging output
* Changes to ‘metadata’ files like pyproject.toml, .gitignore, build scripts, etc.
* Moving source files from one directory or package to another

# How to Report a Bug
If you find a security vulnerability, do NOT open an issue. Email dan@yeaw.me instead.

When filing an issue, make sure to answer the questions in the issue template.

1. What version are you using? 
2. What operating system are you using?
3. What did you do?
4. What did you expect to see?
5. What did you see instead?

# How to Suggest a Feature or Enhancement
If you find yourself wishing for a feature that doesn't exist in Gaphor,
you are probably not alone. There are bound to be others out there with similar
needs. Many of the features that Gaphor has today have been added
because our users saw the need. Open an issue on our issues list on GitHub
which describes the feature you would like to see, why you need it, and how it
should work.

# Code review process

The core team looks at Pull Requests on a regular basis, you should expect a
response within a week. After feedback has been given we expect responses
within two weeks. After two weeks we may close the pull request if it isn't
showing any activity.


# Community
You can chat with the Gaphor community on gitter: https://gitter.im/Gaphor/Lobby.

