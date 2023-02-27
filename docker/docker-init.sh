#!/usr/bin/env bash

set -e

STEP_CNT=2

echo_step() {
cat <<EOF

######################################################################


Init Step ${1}/${STEP_CNT} [${2}] -- ${3}


######################################################################

EOF
}

# Initialize the database
echo_step "1" "Starting" "Applying DB migrations"
# flask db migrate || true
flask db upgrade head
echo_step "1" "Complete" "Applying DB migrations"

echo_step "2" "Starting" "Cleaning cache"
flask cache clean
echo_step "2" "Complete" "Cleaning cache"
