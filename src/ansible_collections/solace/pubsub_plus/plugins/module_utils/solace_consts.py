# Copyright (c) 2021, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_sys as solace_sys


class SolaceTaskOps(object):

    OP_READ_SEMP_VERSION = 'read_semp_version'
    OP_READ_OBJECT_LIST = 'read_object_list'
    OP_READ_OBJECT = 'read_object'
    OP_CREATE_OBJECT = 'create_object'
    OP_DELETE_OBJECT = 'delete_object'
    OP_UPDATE_OBJECT = 'update_object'
