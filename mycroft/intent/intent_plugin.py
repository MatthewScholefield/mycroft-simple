# Copyright (c) 2019 Mycroft AI, Inc. and Matthew Scholefield
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
from typing import List, Any

from mycroft.plugin.base_plugin import BasePlugin
from mycroft.intent_match import IntentMatch
from mycroft.plugin.option_plugin import MustOverride


class DynamicEntity:
    def __init__(self, name: str, data: List[str]):
        self.name = name
        self.data = data

    def __str__(self):
        return self.name


class DynamicIntent:
    def __init__(self, name: str, data: List[str]):
        self.name = name
        self.data = data

    def __str__(self):
        return self.name


class IntentPlugin(BasePlugin):
    """Interface for intent engines"""

    def __init__(self, rt):
        super().__init__(rt)

    def register(self, intent: Any, skill_name: str, intent_id: str):
        """
        Registers a new intent with the intent engine

        Args:
            intent: Arbitrary, engine-specific object used to create the intent
            skill_name: snake case name of skill without _skill suffix
            intent_id: Unique identifier for the intent
        """
        raise MustOverride

    def register_entity(self, entity: Any, skill_name: str, entity_id: str):
        """
        Registers a new entity with the intent engine

        Args:
            entity: Arbitrary, engine-specific object used to create the intent
            skill_name: snake case name of skill without _skill suffix
            entity_id: Unique identifier for the intent
        """
        raise MustOverride

    def unregister(self, intent_id: str):
        """Remove the registered intent from the intent engine"""
        raise MustOverride

    def unregister_entity(self, entity_id: str):
        """Remove the registered intent from the intent engine"""
        raise MustOverride

    def calc_intents(self, query: str) -> List[IntentMatch]:
        """
        Run the intent engine to determine the probability of each intent against the query
        Args:
            query: input sentence as a single string
        Returns:
            intent matches: describes how the intent engine matched each intent with the query
        """
        raise MustOverride

    def compile(self):
        """Callback run when all intents have been registered"""
        pass
