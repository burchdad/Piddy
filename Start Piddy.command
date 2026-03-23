#!/usr/bin/env bash
# Double-click this file on macOS to launch Piddy
# It opens Terminal.app and runs start.sh
cd "$(dirname "$0")"
exec ./start.sh "$@"
