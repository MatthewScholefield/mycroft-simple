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
from threading import Timer

from mycroft.configuration import ConfigurationManager


class IntentName:
    def __init__(self, skill='', intent=''):
        self.skill = skill
        self.intent = intent

    def __str__(self):
        return self.skill + ':' + self.intent

    def __eq__(self, other):
        return self.skill == other.skill and self.intent == other.intent

    @classmethod
    def from_str(cls, str):
        parts = str.split(':')
        return cls(parts[0], parts[1])


class SkillResult:
    def __init__(self, name=IntentName(), results=[], actions=[], confidence=0.0):
        self.name = name
        self.data = results
        self.actions = actions
        self.confidence = confidence

    def set_name(self, name):
        self.name = name
        return self


class MycroftSkill:
    """Base class for all Mycroft skills"""

    def __init__(self, path_manager, intent_manager, query_manager):
        self.path_manager = path_manager
        self._intent_manager = intent_manager
        self._query_manager = query_manager
        self._results = {}
        self._actions = []
        self._ignore_data = False

        self.global_config = ConfigurationManager.get()
        self.config = ConfigurationManager.load_skill_config(self.skill_name,
                                                             self.path_manager.skill_conf(self.skill_name))

    def _create_handler(self, handler):
        def custom_handler(intent_data):
            """
            Runs the handler and generates SkillResult to return
            Returns:
                result (SkillResult): data retrieved from API by the skill
            """
            result = SkillResult()
            self._results.clear()
            self._actions.clear()
            result.confidence = handler(intent_data)
            if result.confidence is None:
                result.confidence = 0.75

            result.data = self._results.copy()
            result.actions = self._actions.copy()
            self._results.clear()
            self._actions.clear()

            if self._ignore_data:
                self._ignore_data = False
                result.data = None

            return result

        return custom_handler

    def send_results(self, intent):
        """Only call outside of a handler to output data"""
        result = SkillResult(IntentName(self.skill_name, intent))
        result.data = self._results.copy()
        result.actions = self._actions.copy()
        if self._ignore_data:
            self._ignore_data = False
            result.data = None
        self._results.clear()
        self._actions.clear()
        self._query_manager.send_result(result)

    @property
    def skill_name(self):
        """Finds name of skill using builtin python features"""
        return self.__class__.__name__

    @property
    def location(self):
        """ Get the JSON data struction holding location information. """
        # TODO: Allow Enclosure to override this for devices that
        # contain a GPS.
        return self.global_config.get('location')

    @property
    def location_pretty(self):
        """ Get a more 'human' version of the location as a string. """
        loc = self.location
        if type(loc) is dict and loc["city"]:
            return loc["city"]["name"]
        return None

    @property
    def location_timezone(self):
        """ Get the timezone code, such as 'America/Los_Angeles' """
        loc = self.location
        if type(loc) is dict and loc["timezone"]:
            return loc["timezone"]["code"]
        return None

    @property
    def lang(self):
        return self.global_config.get('lang')

    def register_intent(self, intent, handler=lambda _: None):
        """
        Set a function to be called when the intent called 'intent' is activated
        In this handler the skill should receive a dict called intent_data
        and call self.add_result() to add output data. Nothing should be returned from the handler
        """
        self._intent_manager.register_intent(self.skill_name, intent, self._create_handler(handler))

    def register_fallback(self, handler):
        """
        Same as register_intent except the handler only receives a query
        and is only activated when all other Mycroft intents fail
        """
        self._intent_manager.register_fallback(self.skill_name, self._create_handler(handler))

    def add_result(self, key, value):
        """
        Adds a result from the skill. For example:
            self.add_result('time', '11:45 PM')
                Except, of course, '11:45 PM' would be something generated from an API

        Results can be both general and granular. Another example:
            self.add_result('time_seconds', 23)
        """
        self._results[str(key)] = str(value).strip()

    def flag_result(self, key):
        """
        Enables a flag (like setting a boolean to true). Example:
            if not_found:
                self.flag_result('not_found')
        """
        self._results[str(key)] = ''

    def add_action(self, action):
        """
        Adds an action to be executed. This can be used to read additional dialog files. For instance:
            if not_paired:
                self.add_action('not.paired')
        
        Args:
            action (str): Name of action to be activated. For instance, corresponds to name of dialog files
        """
        self._actions.append(IntentName(self.skill_name, action))

    def set_action(self, action):
        """
        Sets the only action to be executed. This can be used
        to change the outputted dialog under certain conditions
        """
        self._actions = [IntentName(self.skill_name, action)]
        self._ignore_data = True


class ScheduledSkill(MycroftSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._delay_s = None  # Delay in seconds
        self.thread = None

    def set_delay(self, delay):
        """Set the delay in seconds"""
        self._delay_s = delay
        self._schedule()

    def on_triggered(self):
        """Override to add behavior ran every {delay_s} seconds"""
        pass

    def _schedule(self):
        """Create the self-sustaining thread that runs on_triggered()"""
        if self.thread:
            self.thread.cancel()
        self.thread = Timer(self._delay_s, self._make_callback())
        self.thread.daemon = True
        self.thread.start()

    def _make_callback(self):
        def callback():
            try:
                self.on_triggered()
            finally:
                self._schedule()

        return callback