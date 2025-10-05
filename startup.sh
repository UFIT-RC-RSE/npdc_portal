#!/bin/bash
#
# ==============================================================================
# Script Name: startup.sh
# Description: This script starts the environment-specific deployment of the    
#              NPDC portal. 'runner.py' manages the workers for the
#              webserver, blastserver, etc.
#
# Usage:       ./startup.sh
#
# Example:
#   ./startup.sh
#
# Author:      TJ Schultz
# Created:     2025-10-04
# Updated:     2025-10-04
# ==============================================================================

# load environment
echo "Loading environment variables..."
if [[ -f "./instance/env.sh" ]]; then
    source ./instance/env.sh
    echo "✅ '$NPDC_ENV' environment loaded from ./instance/env.sh"
else
    echo "❌ Environment file not found!"
    echo "Please create: cp ./env.sh.template ./instance/env.sh"
    echo "Then edit ./instance/env.sh with environment settings"
    exit 1
fi

# loaded environment; starting runner
echo "Starting NPDC runner - ($NPDC_ENV)..."

python ./runner/runner.py
