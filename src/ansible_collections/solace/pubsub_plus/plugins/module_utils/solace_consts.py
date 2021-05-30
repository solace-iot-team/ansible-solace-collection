# Copyright (c) 2021, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys
import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_module_ops_consts as MODULE_OPS


class SolaceTaskOps(object):

    OP_READ_SEMP_VERSION = MODULE_OPS.MODULE_OP_READ_SEMP_VERSION
    OP_READ_OBJECT_LIST = MODULE_OPS.MODULE_OP_READ_OBJECT_LIST
    OP_READ_OBJECT = MODULE_OPS.MODULE_OP_READ_OBJECT
    OP_CREATE_OBJECT = MODULE_OPS.MODULE_OP_CREATE_OBJECT
    OP_DELETE_OBJECT = MODULE_OPS.MODULE_OP_DELETE_OBJECT
    OP_UPDATE_OBJECT = MODULE_OPS.MODULE_OP_UPDATE_OBJECT
