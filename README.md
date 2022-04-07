A command-line tool to detect potential burn-out situations from Git repositories.

# Features

Core features:

- [x] Extract data about contributors to one or more Git repositories
- [x] Find out of office / work hours contributions using a set of predefined rules
- [x] Compute an "out of work contribution rate" (OoWCR) per contributor
- [x] Present the data in a user friendly format

Nice to have:

- [x] Custom sorting order (total commits, contributor, overtime ratio) / reverse
- [x] Restrict data to selected contributors
- [x] Collect data for a specific time frame only (e.g 3 months)
- [x] Configurable work days and times
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
burnout-sentry report --help
# or
python3 burnout_sentry/__init__.py report --help
# or
python3 -m burnout_sentry report --help
```

# Usage

```bash
# clone a few repositories you want to extract data from
git clone https://git.entrouvert.org/passerelle.git /tmp/passerelle
git clone https://git.entrouvert.org/combo-plugin-gnm.git/ /tmp/combo-plugin-gnm
git clone https://git.entrouvert.org/authentic.git/ /tmp/authentic

# Get a basic report from a single repository
burnout-sentry report /tmp/passerelle

# Get a report from a single repository, sorted by contributor email
burnout-sentry report --sort contributor /tmp/passerelle

# Get a report including data from multiple repositories
burnout-sentry report \
    /tmp/passerelle \
    /tmp/combo-plugin-gnm \
    /tmp/authentic

# Show the 3 contributors with the most overtime commits
burnout-sentry report \
    --sort overtime_commits \
    --reverse \
    --limit 3 \
    /tmp/passerelle 

# Show the 3 contributors with the greatest overtime commits ratio
burnout-sentry report \
    --sort overtime_ratio \
    --reverse \
    --limit 3 \
    /tmp/passerelle 

# Show results for first quarter of 2021
burnout-sentry report \
    --after 2021-01-01 \
    --before 2021-03-31 \
    /tmp/passerelle 

# Show results matching specific emails
burnout-sentry report \
    --match fpeters \
    --match vdeniaud \
    /tmp/passerelle 

# Show result with a custom work time configuration:
# - Days start at 09:30
# - Days end at 17:30
# - Fridays, saturdays and sundays are off
burnout-sentry report \
    --work-start 09:30 \
    --work-end 17:30 \
    --off-weekday 4 \
    --off-weekday 5 \
    --off-weekday 6 \
    /tmp/passerelle 

# Output results in github markdown format
burnout-sentry report --format github /tmp/passerelle 

# Output results in JSON format and get the total number
# of overtime commits using jq
burnout-sentry report --format json /tmp/passerelle  | jq '[.[].overtime_commits] | add'
```

# Running tests

```bash
pytest
```
