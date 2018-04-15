# Copyright (c) 2017 Mycroft AI, Inc.
#
# This file is part of Mycroft Light
# (see https://github.com/MatthewScholefield/mycroft-light).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from abc import ABCMeta

from typing import TYPE_CHECKING

from mycroft.util import log

if TYPE_CHECKING:
    from mycroft.root import Root


class BasePlugin(metaclass=ABCMeta):
    """Any dynamically loaded class"""
    _plugin_path = ''
    _attr_name = ''
    _package_struct = {}

    def __init__(self, rt):
        self.rt = rt  # type: Root

        self.config = rt.config if 'config' in rt else {}

        for parent in self._plugin_path.split('.'):
            self.config = self.config.get(parent, {})

        if self._package_struct:
            self.rt.package.add_struct(self._package_struct)
