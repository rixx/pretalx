#!/bin/bash
# .claude/hooks/session-start.sh

# Install bd globally (only takes a few seconds)
# echo "Installing bd (beads issue tracker)..."

# npm install -g @beads/bd  # wouldn't it be fun if this worked?

command -v bd && exit 0

git clone https://github.com/steveyegge/beads.git /tmp/beads-repo --depth 1
cd /tmp/beads-repo && go build -o /usr/local/bin/bd ./cmd/bd
