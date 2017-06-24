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
class MycroftSkill:
    """Base class for all Mycroft skills"""

    def __init__(self, path_manager, intent_manager):
        self.path_manager = path_manager
        self._intent_manager = intent_manager
        self._results = {}

    def _create_handler(self, handler, skill_name=None):
        """Wrap the skill handler to return added results"""

        def custom_handler(intent_data):
            self._results.clear()
            handler(intent_data)
            if skill_name is not None:
                self._results['skill_name'] = skill_name
            return self._results

        return custom_handler

    @property
    def skill_name(self):
        """Finds name of skill using builtin python features"""
        return self.__class__.__name__

    def register_intent(self, name, handler=lambda _:{}):
        """
        Set a function to be called when the intent called 'name' is activated
        In this handler the skill should receive a dict called intent_data
        and call self.add_result() to add output data. Nothing should be returned from the handler
        """
        self._intent_manager.register_intent(self.skill_name, name, self._create_handler(handler))

    def register_fallback(self, handler):
        """
        Same as register_intent except the handler only receives a query
        and is only activated when all other Mycroft intents fail
        """
        self._intent_manager.register_fallback(self._create_handler(handler, self.skill_name))

    def add_result(self, key, value):
        """
        Adds a result from the skill. For example:
            self.add_result('time', '11:45 PM')
                Except, of course, '11:45 PM' would be something generated from an API

        Results can be both general and granular. Another example:
            self.add_result('time_seconds', 23)
        """
        self._results[str(key)] = str(value).strip()
