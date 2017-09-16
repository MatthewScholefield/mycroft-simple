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
import sys
from os import listdir
from os.path import isdir, join, dirname
from subprocess import call

from threading import Thread

from mycroft.skill import MycroftSkill
from mycroft.util import to_camel, LOG
from mycroft.util.git_repo import GitRepo


class SkillManager:
    """Dynamically loads skills"""

    def __init__(self, path_manager, intent_manager, query_manager):
        MycroftSkill.initialize_references(path_manager, intent_manager, query_manager)
        self.path_manager = path_manager
        self.skills = []
        self.git_repo = GitRepo(directory=self.path_manager.skills_dir,
                                url='https://github.com/MatthewScholefield/mycroft-simple.git',
                                branch='skills',
                                update_freq=1)

    def load_skill(self, skill_name):
        cls_name = to_camel(skill_name)
        print('Loading ' + cls_name + '...')
        try:
            skill = None
            exec('from ' + skill_name + '.skill import ' + cls_name)
            exec('skill = ' + cls_name + '()')
            self.skills.append(skill)

        except Exception as e:
            LOG.print_e(e, 'loading ' + skill_name)
            print('Failed to load ' + skill_name + '!')

    def load_skills(self):
        """
        Looks in the skill folder and loads the
        CamelCase equivalent class of the snake case folder
        This class should be inside the skill.py file. Example:

        skills/
            time_skill/
                skill.py - class TimeSkill(MycroftSkill):
            weather_skill/
                skill.py - class WeatherSkill(MycroftSkill):
        """

        # Temporary while skills are monolithic
        skills_dir = self.path_manager.skills_dir
        if isdir(skills_dir) and not isdir(join(skills_dir, '.git')):
            call(['mv', skills_dir, join(dirname(skills_dir), 'skills-old')])

        self.git_repo.try_pull()
        # End temporary

        threads = []
        sys.path.append(self.path_manager.skills_dir)
        skill_names = listdir(self.path_manager.skills_dir)
        for skill_name in skill_names:
            if not re.match('^[a-z][a-z_]*_skill$', skill_name):
                continue

            t = Thread(target=lambda: self.load_skill(skill_name),
                   daemon=True)
            t.start()
            threads.append(t)
        for i in threads:
            i.join()
        print('All skills loaded.')
        print()
