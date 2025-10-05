#!/bin/bash
#
# ==============================================================================
# Script Name: init_db.sh
# Description: This script performs the npdc_portal.db ->
#              npdc_portal_searchable.db initialization step; necessary for when
#              npdc_portal.db is updated. Run this before deployment in /.
#
# Usage:       ./init_db.sh
#
# Example:
#   ./init_db.sh
#
# Author:      TJ Schultz
# Created:     2025-10-04
# Updated:     2025-10-04
# ==============================================================================

# get script dir (root of project - /) dir
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTANCE_DB_DIR="$SCRIPT_DIR/instance/db_data"

python "$SCRIPT_DIR/flask_app/init_db.py"
cp "$INSTANCE_DB_DIR/npdc_portal.db" "$INSTANCE_DB_DIR/npdc_portal_searchable.db"
python "$SCRIPT_DIR/flask_app/init_db_searchable.py"
