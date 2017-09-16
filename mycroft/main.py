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

from mycroft.clients.enclosure_client import EnclosureClient
from mycroft.clients.websocket_client import WebsocketClient

sys.path.append(os.path.abspath('.'))

from mycroft.api import is_paired
from mycroft.configuration import ConfigurationManager
from mycroft.clients.speech_client import SpeechClient
from mycroft.clients.text_client import TextClient
from mycroft.managers.client_manager import ClientManager
from mycroft.managers.format_manager import FormatManager
from mycroft.managers.intent_manager import IntentManager
from mycroft.managers.path_manager import PathManager
from mycroft.managers.query_manager import QueryManager
from mycroft.managers.skill_manager import SkillManager
from mycroft.util import LOG
from mycroft import main_thread


def try_pair():
    try:
        from mycroft.skills.pairing_skill.skill import PairingSkill
        if not is_paired():
            PairingSkill.start_pairing()
    except ImportError:
        pass


def main():
    ConfigurationManager.init()
    LOG.init(ConfigurationManager.get())

    if len(sys.argv) > 1:
        letters = ''.join(sys.argv[1:]).lower()
    else:
        letters = 'wtse'
    clients = []
    for c, cls in [
        ('w', WebsocketClient),
        ('t', TextClient),
        ('s', SpeechClient),
        ('e', EnclosureClient)
    ]:
        if c in letters:
            clients.append(cls)
    msg = 'Starting clients: ' + ', '.join(cls.__name__ for cls in clients)
    print(msg)
    LOG.debug(msg)

    path_manager = PathManager()
    intent_manager = IntentManager(path_manager)
    format_manager = FormatManager(path_manager)
    query_manager = QueryManager(intent_manager, format_manager)
    skill_manager = SkillManager(path_manager, intent_manager, query_manager)

    LOG.debug('Starting clients...')
    client_manager = ClientManager(clients, path_manager, query_manager, format_manager)
    LOG.debug('Started clients.')

    skill_manager.load_skills()
    LOG.debug('Loaded skills.')
    intent_manager.on_intents_loaded()
    LOG.debug('Executed on intents loaded callback.')
    try_pair()
    LOG.debug('Checked pairing.')

    client_manager.start()
    try:
        LOG.debug('Waiting to quit...')
        main_thread.wait_for_quit()
    finally:
        LOG.debug('Quiting!')
        client_manager.on_exit()


if __name__ == "__main__":
    main()
