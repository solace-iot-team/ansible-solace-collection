# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import os
import logging
from distutils.util import strtobool

_SC_SYSTEM_ERR_RC = -1

################################################################################################
# check python version
_PY3_MIN = sys.version_info[:2] >= (3, 6)
if not _PY3_MIN:
    print(
        '\n{"failed": true, "rc": %d, "msg_hint": "Set ANSIBLE_PYTHON_INTERPRETER=path-to-python-3", '
        '"msg": "solace.pubsub_plus requires a minimum of Python3 version 3.6. Current version: %s."}' % (_SC_SYSTEM_ERR_RC, ''.join(sys.version.splitlines()))
    )
    sys.exit(1)

################################################################################################
# initialize logging
ENABLE_LOGGING = False
enableLoggingEnvVal = os.getenv('ANSIBLE_SOLACE_ENABLE_LOGGING')
loggingPathEnvVal = os.getenv('ANSIBLE_SOLACE_LOG_PATH')
if enableLoggingEnvVal is not None and enableLoggingEnvVal != '':
    try:
        ENABLE_LOGGING = bool(strtobool(enableLoggingEnvVal))
    except ValueError as e:
        # note: from e ==> import error python 2.7
        raise ValueError("failed: invalid value for env var: 'ANSIBLE_SOLACE_ENABLE_LOGGING={enableLoggingEnvVal}'. use 'true' or 'false' instead.") from e

if ENABLE_LOGGING:
    logFile = './ansible-solace.log'
    if loggingPathEnvVal is not None and loggingPathEnvVal != '':
        log_path = os.path.dirname(loggingPathEnvVal)
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        logFile = loggingPathEnvVal
    logging.basicConfig(filename=logFile,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s(): %(message)s')
    logging.info('Module start #############################################################################################')
