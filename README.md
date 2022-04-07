A command-line tool to detect potential burn-out situations from Git repositories.

# Features

Core features:

- [x] Extract data about contributors to one or more Git repositories
- [x] Find out of office / work hours contributions using a set of predefined rules
- [x] Compute an "out of work contribution rate" (OoWCR) per contributor
- [x] Present the data in a user friendly format

Nice to have:

- [x] Custom sorting order (total commits, contributor, overtime ratio) / reverse
- [ ] Restrict data to selected contributors
- [x] Collect data for a specific time frame only (e.g 3 months)
- [ ] Show evolution of results compared to another period
- [x] Output to a machine-oriented format (e.g JSON) for easier manipulation by other scripts and tools
- [ ] Timezone handling


# Installation

These tools and packages are required before installing `burnout-sentry`:

- git (`sudo apt install git` if you're using a Debian-based distribution)
- Python 3.9 or greater (earlier Python 3 versions should work but are untested)
- pip

Other requirements are taken care of automatically when `burnout-sentry` is installed via pip.

```bash
# Get the code
git clone https://github.com/agateblue/burnout-sentry.git
cd burnout-sentry

# Install burnout-sentry and its dependencies
# in editable mode, for development
pip3 install --user -e '.[dev]'

# at this point, you should be able to use burnout-sentry
burnout-sentry --help
```

# Usage

```bash
# clone a repository you want to extract data from
git clone https://git.entrouvert.org/passerelle.git /tmp/passerelle

# Get a standard report
burnout-sentry report /tmp/passerelle
```

# Running tests

```bash
pytest
```
