#!/usr/bin/env sh
set -eu

export PYTHONPATH="/app/src"
export FAMILY_MENU_STATIC="${FAMILY_MENU_STATIC:-/app/src/family_menu/static}"

exec /opt/family-menu/bin/python3 -m family_menu
