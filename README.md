A command-line tool to detect potential burn-out situations from Git repositories.

# Features

Core features:

- [ ] Extract data about contributors to one or more Git repositories
- [ ] Find out of office / work hours contributions using a set of predefined rules
- [ ] Compute an "out of work contribution rate" (OoWCR) per contributor
- [ ] Present the data in a user friendly format

Nice to have:

- [ ] Restrict data to selected contributors
- [ ] Collect data for a specific time frame only (e.g 3 months)
- [ ] Show evolution of results compared to another period
- [ ] Output to a machine-oriented format (e.g JSON) for easier manipulation by other scripts and tools

# Installation

Requirements:

- git (`sudo apt install git` if you're using a Debian-based distribution)
- Python 3.9 or greater (earlier Python 3 versions should work but are untested)
- pip

Then:

```bash
git clone https://github.com/agateblue/burnout-sentry.git
cd burnout-sentry

pip3 install --user '.[dev]'

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

