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


class IntentManager:
    """Used to handle creating both intents and intent engines"""

    def __init__(self, path_manager):
        self.engines = [i(path_manager) for i in engine_classes]
        self.handlers = {}
        self.fallbacks = []

    def register_intent(self, skill_name, intent, handler):
        """
        Register an intent via the corresponding intent engine
        It tries passing the arguments to each engine until one can interpret it correctly

        Note: register_intent in the MycroftSkill base class automatically creates a SkillResult
        Args:
            skill_name (str):
            intent (obj): argument used to build intent; can be anything
            handler (obj): function that receives a SkillMatch and returns a SkillResult


        """
        for i in self.engines:
            intent_name = i.try_register_intent(skill_name, intent)
            if intent_name is not None:
                self.handlers[str(intent_name)] = lambda match: handler(match).set_name(intent_name)
                return
        print("Failed to register intent for " + str(IntentName(skill_name, str(intent))))

    def register_fallback(self, skill_name, handler):
        """
        Register a function to be called as a general knowledge fallback

        Args:
            handler (obj): function that receives query and returns a SkillResult
                        note: register_fallback in the MycroftSkill base class automatically generates a SkillResult
        """
        name = IntentName(skill_name, 'fallback')
        self.fallbacks.append(lambda match: handler(match).set_name(name))

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
        skill_results = []
        for match in to_test:
            skill_result = self.handlers[str(match.name)](match)
            skill_result.confidence = sqrt(match.confidence * skill_result.confidence)
            skill_results.append(skill_result)

        if len(skill_results) > 0:
            best = max(enumerate(skill_results), key=lambda x: x[1].confidence)[1]
            if best.confidence > 0.5:
                return best

        fallback_results = [fallback(query) for fallback in self.fallbacks]
        best = max(enumerate(fallback_results), key=lambda x: x[1].confidence)[1]
        return best
