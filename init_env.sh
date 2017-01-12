#!/bin/sh

# This script is used to setup environment variables to use for development
# Call this script before running 'flask run'

export PYTHONPATH="$PWD"
export FLASK_APP="main.py"
export FLASK_DEBUG=1