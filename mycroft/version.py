#
# Copyright (c) 2017 Mycroft AI, Inc.
#
# This file is part of Mycroft Simple
# (see https://github.com/MatthewScholefield/mycroft-simple).
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
#
import json
from genericpath import exists, isfile

from mycroft.util import logger

# The following lines are replaced during the release process.
# START_VERSION_BLOCK
CORE_VERSION_MAJOR = 0
CORE_VERSION_MINOR = 8
CORE_VERSION_BUILD = 16
# END_VERSION_BLOCK

CORE_VERSION_STR = (str(CORE_VERSION_MAJOR) + "." +
                    str(CORE_VERSION_MINOR) + "." +
                    str(CORE_VERSION_BUILD))


class VersionManager:
    __location = "/opt/mycroft/version.json"

    @staticmethod
    def get():
        if (exists(VersionManager.__location) and
                isfile(VersionManager.__location)):
            try:
                with open(VersionManager.__location) as f:
                    return json.load(f)
            except:
                logger.error("Failed to load version from '%s'"
                             % VersionManager.__location)
        return {"coreVersion": None, "enclosureVersion": None}