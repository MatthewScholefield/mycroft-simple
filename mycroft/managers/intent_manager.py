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
from mycroft.engines.intent_engine import make_namespaced
from mycroft.engines.padatious_engine import PadatiousEngine

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

        Note: register_intent in the MycroftSkill base class automatically manages results
        Args:
            skill_name (str):
            intent (obj): argument used to build intent; can be anything
            handler (obj): function that receives intent_data and returns a dict of results


        """
        for i in self.engines:
            intent_name = i.try_register_intent(skill_name, intent)
            if intent_name != "":
                self.handlers[intent_name] = handler
                return
        print("Failed to register intent for " + make_namespaced(str(intent), skill_name))

    def register_fallback(self, handler):
        """
        Register a function to be called as a general knowledge fallback

        Args:
            handler (obj): function that receives query and returns a
                        dict of results, one of which is 'confidence'
                        note: register_fallback in the MycroftSkill base class automatically manages results
        """
        self.fallbacks.append(handler)

    def on_intents_loaded(self):
        for i in self.engines:
            i.on_intents_loaded()

    def calc_results(self, query):
        """
        Find the best intent and run the handler to find the results

        Args:
            query (str): input sentence
        Returns:
            name (str): namespaced intent
            results (dict) : dictionary of the possible intent results
        """

        query = query.strip()

        # A single intent result is a dict like the following example:
        # { 'name': 'TimeSkill:time.ask', 'confidence': '0.65', 'matches': {'location': 'new york'} }
        intent_results = {}

        def merge_results(new_intent_results):
            """Merge new intent results with old ones, keeping ones with higher confidences"""
            for skill, data in new_intent_results.items():
                if skill in intent_results and intent_results[skill]['confidence'] > data['confidence']:
                    continue
                intent_results[skill] = data

        for i in self.engines:
            merge_results(i.calc_intents(query))

        sorted_intents = [val for key, val in sorted(intent_results.items(),
                                                     key=lambda kv: kv[1]['confidence'], reverse=True)]
        intent_data = sorted_intents[0]
        if intent_data['confidence'] > 0.5:
            name = intent_data['name']
            results, actions = self.handlers[name](intent_data)
        else:
            best_results = {'confidence': '0.0'}
            best_actions = []
            for fallback in self.fallbacks:
                results, actions = fallback(query)
                if float(results['confidence']) > float(best_results['confidence']):
                    best_results = results
                    best_actions = actions

            name = 'UnknownSkill:unknown'
            results = {}
            actions = []

            if float(best_results['confidence']) > 0.5:
                name = make_namespaced('fallback', best_results['skill_name'])
                results = best_results
                actions = best_actions

        return name, results, actions
