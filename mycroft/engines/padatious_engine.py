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
from mycroft.engines.intent_engine import IntentEngine, IntentMatch
from mycroft.skill import IntentName
from padatious import IntentContainer

from mycroft.util import LOG


class PadatiousEngine(IntentEngine):
    """Interface for Padatious intent engine"""

    def __init__(self, path_manager):
        super().__init__(path_manager)
        self.container = IntentContainer(path_manager.intent_cache)

    def try_register_intent(self, skill_name, intent_name):
        if not isinstance(intent_name, str):
            return None
        intent_dir = self.path_manager.intent_dir(skill_name)
        file_name = os.path.join(intent_dir, intent_name + '.intent')
        if not os.path.isfile(file_name):
            return None

        name = IntentName(skill_name, intent_name)
        self.container.load_file(str(name), file_name)
        return name

    def on_intents_loaded(self):
        print('Training...')
        LOG.info('Training...')
        self.container.train()
        LOG.info('Training complete!')
        print('Training complete!')
        print()

    def calc_intents(self, query):
        matches = []
        for data in self.container.calc_intents(query):
            matches.append(IntentMatch(name=IntentName.from_str(data.name),
                                       confidence=data.conf,
                                       matches=data.matches,
                                       query=query))

        return matches
