#!/usr/bin/env python3
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

import os
import sys

sys.path.append(os.path.abspath('.'))

from mycroft import mycroft_thread
from mycroft.api import is_paired
from mycroft.configuration import ConfigurationManager
from mycroft.clients.text_client import TextClient
from mycroft.managers.client_manager import ClientManager
from mycroft.managers.format_manager import FormatManager
from mycroft.managers.intent_manager import IntentManager
from mycroft.managers.path_manager import PathManager
from mycroft.managers.query_manager import QueryManager
from mycroft.managers.skill_manager import SkillManager
from mycroft.util import init_logging


def try_pair():
    try:
        from mycroft.skills.pairing_skill.skill import PairingSkill
        if not is_paired():
            PairingSkill.start_pairing()
    except ImportError:
        pass


def main():
    init_logging(ConfigurationManager.get())

    path_manager = PathManager(os.getcwd())
    intent_manager = IntentManager(path_manager)
    format_manager = FormatManager(path_manager)
    query_manager = QueryManager(intent_manager, format_manager)
    skill_manager = SkillManager(intent_manager, path_manager, query_manager)
    client_manager = ClientManager([TextClient], query_manager)

    skill_manager.load_skills()
    intent_manager.on_intents_loaded()

    try_pair()

    client_manager.start()
    mycroft_thread.set_quit_action(client_manager.quit)


if __name__ == "__main__":
    main()
