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
from abc import ABCMeta, abstractmethod


def make_namespaced(intent_name, skill_name):
    """Mangle the intent name so that it doesn't conflict and to save the skill name in the same string"""
    return skill_name + ':' + intent_name


def extract_skill_name(namespaced_name):
    """Ex. TimeSkill:time.ask -> TimeSkill"""
    return namespaced_name.split(':')[0]


def extract_intent_name(namespaced_name):
    """Ex. TimeSkill:time.ask -> time.ask"""
    return namespaced_name.split(':')[1]


class IntentEngine(metaclass=ABCMeta):
    """Interface for intent engines"""

    def __init__(self, path_manager):
        self.path_manager = path_manager

    @abstractmethod
    def try_register_intent(*args, **kwargs):
        """
        Attempt to register intent with given arguments
        Returns:
            name (str): intent name if parsed parameters, otherwise ""
        """
        pass

    @abstractmethod
    def calc_intents(self, query):
        """
        Run the intent engine to determine the probability of each intent against the query
        Args:
            query (str): input sentence as a single string
        Returns:
            intent (dict): intent_data where

        Example return data:
        { 'name': 'TimeSkill:time.ask', 'confidence': '0.65', 'matches': {'location': 'new york'} }
        """
        pass

    def on_intents_loaded(self):
        """Override to run code when all intents have been registered"""
        pass
