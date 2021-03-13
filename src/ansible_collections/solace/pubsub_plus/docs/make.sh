#!/usr/bin/env bash
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

make --makefile ./Makefile.custom docs
  code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - $code make docs"; exit 1; fi

make linkcheck
  code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - $code make linkcheck"; exit 1; fi

make --makefile ./Makefile.custom clean docs
  code=$?; if [[ $code != 0 ]]; then echo ">>> ERROR - $code make docs"; exit 1; fi

###
# The End.
