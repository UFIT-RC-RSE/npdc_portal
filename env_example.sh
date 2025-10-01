#!/bin/bash

# =============================================================================
# NPDC Portal - Environment Variables Example
# =============================================================================
# This script shows how to set environment variables for sensitive configuration
# Copy this file and customize it for your environment
# NEVER commit this file with actual secrets to Git

# Captcha
export RECAPTCHA_SITE_KEY="your-captcha-sitekey"

# NPDC environment
export NPDC_ENVIRONMENT=${1:-'dev'}

echo "Environment variables set for the NPDC Portal"
echo "Current environment: ${NPDC_ENVIRONMENT:-'NOT SET'}"
