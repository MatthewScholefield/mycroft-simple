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
from os.path import join, dirname, abspath, isfile
from threading import Timer, Event

import sys

from mycroft.configuration import ConfigurationManager
from mycroft.util import logger
from inspect import signature


class IntentName:
    def __init__(self, skill='', intent=''):
        self.skill = skill
        self.intent = intent

    def __bool__(self):
        return bool(self.skill) or bool(self.intent)

    def __str__(self):
        return self.skill + ':' + self.intent

    def __eq__(self, other):
        return self.skill == other.skill and self.intent == other.intent

    @classmethod
    def from_str(cls, str):
        parts = str.split(':')
        return cls(parts[0], parts[1])


class SkillResult:
    def __init__(self, name=IntentName(), data=[], action=None, callback=None, confidence=0.0):
        self.name = name
        self.data = data
        self.action = action
        self.callback = callback
        self.confidence = confidence


class MycroftSkill:
    """Base class for all Mycroft skills"""

    def __init__(self):
        self._results = {}
        self._action = None
        self._callback = None
        self._intent_name = None

        self.global_config = ConfigurationManager.get()
        self.config = ConfigurationManager.load_skill_config(self.skill_name,
                                                             self.path_manager.skill_conf(self.skill_name))

    @classmethod
    def initialize_references(cls, path_manager, intent_manager, query_manager):
        cls.path_manager = path_manager
        cls._intent_manager = intent_manager
        cls._query_manager = query_manager

    def _reset_state(self):
        self._results.clear()
        self._callback = self.__make_callback()
        self._action = None

    def _create_handler(self, handler):
        def custom_handler(intent_match):
            """
            Runs the handler and generates SkillResult to return
            Returns:
                confidence (float): confidence of data retrieved by API
            """
            self._reset_state()
            try:
                if len(signature(handler).parameters) == 1:
                    conf = handler(intent_match)
                else:
                    conf = handler()
            except Exception as e:
                logger.print_e(e, self.skill_name)
                conf = 0
            if conf is None:
                conf = 0.75
            return conf

        return custom_handler

    def _file_name(self, file):
        return join(dirname(abspath(sys.modules[self.__class__.__module__].__file__)), file)

    def open_file(self, file, *args, **kwargs):
        return open(self._file_name(file), *args, **kwargs)

    def is_file(self, file):
        return isfile(self._file_name(file))

    def _package_results(self, intent_name=IntentName()):
        result = SkillResult(intent_name, data=self._results.copy(), action=self._action)
        if result.action is None:
            result.action = intent_name

        self._reset_state()
        return result

    def trigger_action(self, default_intent, get_results=None):
        """Only call outside of a handler to output data"""
        if get_results is not None:
            self._create_handler(get_results)(None)
        result = self._package_results()
        if not result.action:
            result.action = IntentName(self.skill_name, default_intent)
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
        self._intent_manager.register_intent(self.skill_name, intent,
                                             self._create_handler(handler), lambda: self._callback())

    def create_alias(self, alias_intent, source_intent):
        """Add another intent that performs the same action as an existing intent"""
        self._intent_manager.create_alias(self.skill_name, alias_intent, source_intent)

    def register_fallback(self, handler):
        """
        Same as register_intent except the handler only receives a query
        and is only activated when all other Mycroft intents fail
        """
        self._intent_manager.register_fallback(self.skill_name, self._create_handler(handler), lambda: self._callback())

    def add_result(self, key, value):
        """
        Adds a result from the skill. For example:
            self.add_result('time', '11:45 PM')
                Except, of course, '11:45 PM' would be something generated from an API

        Results can be both general and granular. Another example:
            self.add_result('time_seconds', )
        """
        self._results[str(key)] = str(value).strip()

    def __make_callback(self, handler=lambda: None):
        """Create a callback that packages and returns the skill result"""
        def callback():
            handler()
            return self._package_results()
        return callback

    def set_action(self, action):
        """
        Sets the only action to be executed. This can be used
        to change the outputted dialog under certain conditions
        """
        self._action = IntentName(self.skill_name, action)

    def set_callback(self, callback):
        self._callback = self.__make_callback(callback)


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
        self.thread = Timer(self._delay_s, self.__make_callback())
        self.thread.daemon = True
        self.thread.start()

    def __make_callback(self):
        def callback():
            try:
                self.on_triggered()
            except Exception as e:
                logger.print_e(e, self.skill_name)
            finally:
                self._schedule()

        return callback
