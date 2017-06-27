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
import re
from os import listdir

import sys

from os.path import isdir, join, dirname

from subprocess import call

from mycroft.util import to_camel


class SkillManager:
    """Dynamically loads skills"""
    GIT_URL = 'https://github.com/MatthewScholefield/mycroft-simple.git'
    GIT_BRANCH = 'skills'

    def __init__(self, intent_manager, path_manager, query_manager):
        self.intent_manager = intent_manager
        self.path_manager = path_manager
        self.query_manager = query_manager
        self.skills = []

    def load_skills(self):
        """
        Looks in the skill folder and loads the CamelCase equivalent class of the snake case folder
        This class should be inside the skill.py file. Example:

        skills/
            time_skill/
                skill.py - class TimeSkill(MycroftSkill):
            weather_skill/
                skill.py - class WeatherSkill(MycroftSkill):
        """
        def cmd(a):
            call(a.split(' '))

        # Temporary while skills are monolithic
        skills_dir = self.path_manager.skills_dir
        if isdir(skills_dir) and not isdir(join(skills_dir, '.git')):
            call(['mv', skills_dir, join(dirname(skills_dir), 'skills-old')])

        if not isdir(self.path_manager.skills_dir):
            call(['git', 'clone', '-b', self.GIT_BRANCH, '--single-branch', self.GIT_URL, skills_dir])
        # End temporary

        sys.path.append(self.path_manager.skills_dir)
        skill_names = listdir(self.path_manager.skills_dir)
        for skill_name in skill_names:
            if not re.match('^[a-z][a-z_]*_skill$', skill_name):
                continue

            cls_name = to_camel(skill_name)
            print('Loading ' + cls_name + '...')

            exec('from ' + skill_name + '.skill import ' + cls_name)
            exec('self.skills.append(' + cls_name + '(self.path_manager, self.intent_manager, self.query_manager))')
        print()
