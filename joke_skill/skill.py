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

import pyjokes

from mycroft import MycroftSkill


class JokeSkill(MycroftSkill):
    def __init__(self):
        super().__init__()
        self.register_intent('joke', self.joke)

    def joke(self):
        lang = self.rt.config['lang'][:-3]
        joke = pyjokes.get_joke(language=lang)
        self.add_result('joke', joke)