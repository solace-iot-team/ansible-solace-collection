#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke, <ricardo.gomez-ulmke@solace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class SolaceError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def to_list(self):
        if isinstance(self.message, list):
            return self.message
        return [str(self.message)]    
