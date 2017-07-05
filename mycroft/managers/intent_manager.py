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
from math import sqrt

from mycroft.engines.intent_engine import IntentMatch
from mycroft.engines.padatious_engine import PadatiousEngine
from mycroft.skill import IntentName

engine_classes = [PadatiousEngine]


class SkillHandler:
    def __init__(self, calc_conf, calc_result, name):
        self.calc_conf = calc_conf
        self.calc_result = self._make_calc_result_fn(calc_result, name)

    def _make_calc_result_fn(self, calc_result, name):
        def callback():
            result = calc_result()
            result.name = name
            if not result.action:
                result.action = name
            return result
        return callback


class IntentManager:
    """Used to handle creating both intents and intent engines"""

    def __init__(self, path_manager):
        self.engines = [i(path_manager) for i in engine_classes]
        self.handlers = {}
        self.fallbacks = []

    def register_intent(self, skill_name, intent, calc_conf_fn, calc_result_fn):
        """
        Register an intent via the corresponding intent engine
        It tries passing the arguments to each engine until one can interpret it correctly

        Note: register_intent in the MycroftSkill base class automatically creates a SkillResult
        Args:
            skill_name (str):
            intent (obj): argument used to build intent; can be anything
            calc_conf_fn (func): function that calculates the confidence
            calc_result_fn (func): function that packages the result once selected
        """
        for i in self.engines:
            intent_name = i.try_register_intent(skill_name, intent)
            if intent_name is not None:
                self.handlers[str(intent_name)] = SkillHandler(calc_conf_fn, calc_result_fn, intent_name)
                return
        print("Failed to register intent for " + str(IntentName(skill_name, str(intent))))

    def create_alias(self, skill_name, alias_intent, intent):
        """
        Register an intent that uses the same handler as another intent
        Args:
            skill_name (str):
            alias_intent (obj): argument used o build intent; can be anything
            intent (str): Name of intent to copy from
        """
        for i in self.engines:
            intent_name = i.try_register_intent(skill_name, alias_intent)
            if intent_name is not None:
                self.handlers[str(intent_name)] = self.handlers[str(IntentName(skill_name, intent))]
                return
        print("Failed to register alias for " + str(IntentName(skill_name, str(intent))))

    def register_fallback(self, skill_name, calc_conf_fn, calc_result_fn):
        """
        Register a function to be called as a general knowledge fallback

        Args:
            calc_conf_fn (obj): function that receives query and returns a SkillResult
                        note: register_fallback in the MycroftSkill base class automatically generates a SkillResult
        """
        name = IntentName(skill_name, 'fallback')
        self.fallbacks.append(SkillHandler(calc_conf_fn, calc_result_fn, name))

    def on_intents_loaded(self):
        for i in self.engines:
            i.on_intents_loaded()

    def calc_result(self, query):
        """
        Find the best intent and run the handler to find the result

        Args:
            query (str): input sentence
        Returns:
            result (SkillResult): object containing data from skill
        """

        query = query.strip().lower()

        # A list of IntentMatch objects
        intent_matches = []

        def merge_matches(new_matches):
            """Merge new matches with old ones, keeping ones with higher confidences"""
            for new_match in new_matches:
                found_match = False
                for i in range(len(intent_matches)):
                    if intent_matches[i].name == new_match.name:
                        intent_matches[i] = IntentMatch.merge(intent_matches[i], new_match)
                        found_match = True
                        break
                if not found_match:
                    intent_matches.append(new_match)

        for i in self.engines:
            merge_matches(i.calc_intents(query))

        to_test = [match for match in intent_matches if match.confidence > 0.5]

        best_conf = 0.0
        best_handler = None
        for match in to_test:
            match.query = query
            handler = self.handlers[str(match.name)]
            conf = sqrt(handler.calc_conf(match) * match.confidence)
            if conf > best_conf:
                best_conf = conf
                best_handler = handler

        if best_conf > 0:
            return best_handler.calc_result()

        best_conf = 0.0
        best_handler = None
        for handler in self.fallbacks:
            conf = handler.calc_conf(query)
            if conf > best_conf:
                best_conf = conf
                best_handler = handler

        return best_handler.calc_result()
