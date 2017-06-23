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
from os.path import join, isfile
from random import randint

from mycroft.engines.intent_engine import extract_skill_name, extract_intent_name
from mycroft.formats.mycroft_format import MycroftFormat


class DialogFormat(MycroftFormat):
    """Format data into sentences"""

    def __init__(self, path_manager):
        """
        Attributes:
            output  The most recent generated sentence
        """
        super().__init__(path_manager)
        self.output = ""

    def generate(self, name, results):
        self.output = ""
        skill_name = extract_skill_name(name)
        intent_name = extract_intent_name(name)
        dialog_dir = self.path_manager.dialog_dir(skill_name)
        dialog_file_name = join(dialog_dir, intent_name + '.dialog')
        if not isfile(dialog_file_name):
            return
        with open(dialog_file_name, 'r') as f:
            lines = f.readlines()
            for key, val in results.items():
                lines = [i.replace('{' + key + '}', val) for i in lines]
            best_lines = [i for i in lines if '{' not in i and '}' not in i]
            if len(best_lines) == 0:
                best_lines = lines

            best_lines = [i.strip() for i in best_lines]

            self.output = best_lines[randint(0, len(best_lines) - 1)]
