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

import math
import sys
from abc import abstractmethod, ABCMeta
from inspect import signature
from os.path import join, dirname, abspath, isfile
from threading import Timer, Event, Thread

from padatious import MatchData

from mycroft.base_plugin import BasePlugin
from mycroft.intent_name import IntentName
from mycroft.result_package import ResultPackage
from mycroft.util import log
from mycroft.util.text import to_snake


class SkillPlugin(BasePlugin):
    """Base class for all Mycroft skills"""

    def __init__(self):
        super().__init__(self.rt)
        self.config = self.rt.config.load_skill_config(self.rt.paths.skill_conf(self.skill_name))

        self._package = self._default_package()
        self._reset_event = Event()
        self._reset_event.set()
        self._average_run_time = 60

    def set_av_run_time(self, time_s):
        self._average_run_time = time_s

    def create_thread(self, target, *args, **kwargs):
        def wrapper(*args, **kwargs):
            try:
                target(*args, **kwargs)
            except:
                self.stop_running()
                log.exception(self.skill_name + ' thread')

        Thread(target=wrapper, daemon=True, *args, **kwargs).start()

    def open_file(self, file, *args, **kwargs):
        """Open file in skill directory"""
        return open(self._file_name(file), *args, **kwargs)

    def is_file(self, file):
        """Check for file in skill directory"""
        return isfile(self._file_name(file))

    def trigger_action(self, default_intent, get_results=None):
        """Only call outside of a handler to output data"""
        if get_results is not None:
            package = self._create_handler(get_results)(None)
        else:
            package = self._package
            self._package = self._default_package()
        if not package.action:
            package.action = IntentName(self.skill_name, default_intent)
        self.rt.query.send_package(package)

    def start_running(self):
        """Indicate that the skill has an ongoing process and should keep UI control"""
        self._reset_event.clear()
        self._package.reset_event = self._reset_event

    def stop_running(self):
        """Indicate that the ongoing job is complete"""
        self._reset_event.set()

    def is_running(self):
        return not self._reset_event.is_set()

    @property
    def skill_name(self):
        """Finds name of skill using builtin python features"""
        return to_snake(self.__class__.__name__).replace('_skill', '')

    @property
    def location(self):
        """ Get the JSON data struction holding location information. """
        # TODO: Allow Enclosure to override this for devices that
        # contain a GPS.
        return self.rt.config['location']

    @property
    def location_pretty(self):
        """ Get a more 'human' version of the location as a string. """
        loc = self.location
        if isinstance(loc, dict) and loc["city"]:
            return loc["city"]["name"]
        return None

    @property
    def location_timezone(self):
        """ Get the timezone code, such as 'America/Los_Angeles' """
        loc = self.location
        if isinstance(loc, dict) and loc["timezone"]:
            return loc["timezone"]["code"]
        return None

    @property
    def lang(self):
        return self.rt.config.get('lang')

    def register_intent(self, intent, handler=lambda _: None):
        """
        Set a function to be called when the intent called 'intent' is activated
        In this handler the skill should receive a dict called intent_data
        and call self.add_result() to add output data. Nothing should be returned from the handler
        """
        self.rt.intent.register_intent(self.skill_name, intent,
                                       self._create_handler(handler))

    def register_entity(self, entity):
        """
        Register a .entity file.
        For example, to register {place}.entity call self.register_entity('{place}')
        """
        self.rt.intent.register_entity(self.skill_name, entity)

    def register_fallback(self, handler):
        """
        Same as register_intent except the handler only receives a query
        and is only activated when all other Mycroft intents fail
        """
        self.rt.intent.register_fallback(self.skill_name, self._create_handler(handler))

    def create_alias(self, alias_intent, source_intent):
        """Add another intent that performs the same action as an existing intent"""
        self.rt.intent.create_alias(self.skill_name, alias_intent, source_intent)

    def add_result(self, key, value):
        """
        Adds a result from the skill. For example:
            self.add_result('time', '11:45 PM')
                Except, of course, '11:45 PM' would be something generated from an API

        Results can be both general and granular. Another example:
            self.add_result('time_seconds', 10)
        Results can also contain any valid json object
        """
        self._package.data[str(key)] = value

    def set_action(self, action):
        """
        Sets the only action to be executed. This can be used
        to change the outputted dialog under certain conditions
        """
        self._package.action = IntentName(self.skill_name, action)

    def set_callback(self, callback):
        self._package.callback = self.__make_callback(callback)

    ############################
    # Private methods
    def _default_package(self):
        return ResultPackage(IntentName(self.skill_name))

    def _create_handler(self, handler):
        def custom_handler(data):
            """
            Runs the handler and generates SkillResult to return
            Returns:
                confidence (float): confidence of data retrieved by API
            """
            self._package = self._default_package()
            if isinstance(data, MatchData):
                self._package.data.assign(data.matches)
            try:
                if len(signature(handler).parameters) == 1:
                    conf = handler(data)
                else:
                    conf = handler()
            except:
                log.exception(self.skill_name)
                conf = 0
            if conf is None:
                if self.is_running():
                    weight = 2 / (1 + math.exp(self._average_run_time / 50.0))
                    conf = 0.75 + 0.25 * weight
                else:
                    conf = 0.75
            self._package.confidence = conf
            package = self._package
            self._package = self._default_package()
            return package

        return custom_handler

    def _file_name(self, file):
        return join(dirname(abspath(sys.modules[self.__class__.__module__].__file__)), file)

    def __make_callback(self, handler=lambda: None):
        """Create a callback that packages and returns the skill result"""

        def callback(package):
            self._package = package
            handler()
            package = self._package
            self._package = self._default_package()
            return package

        return callback


class ScheduledSkill(SkillPlugin, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self._delay_s = None  # Delay in seconds
        self._thread = None

    def set_delay(self, delay):
        """Set the delay in seconds"""
        self._delay_s = delay
        self._schedule()

    @abstractmethod
    def on_triggered(self):
        """Override to add behavior ran every {delay_s} seconds"""
        pass

    def _schedule(self):
        """Create the self-sustaining thread that runs on_triggered()"""
        if self._thread:
            self._thread.cancel()
        self._thread = Timer(self._delay_s, self.__make_callback())
        self._thread.daemon = True
        self._thread.start()

    def __make_callback(self):
        def callback():
            try:
                self.on_triggered()
            except:
                log.exception(self.skill_name)
            finally:
                self._schedule()

        return callback