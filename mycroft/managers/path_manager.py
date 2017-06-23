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
from os.path import join

from mycroft.util import to_snake


class PathManager:
    """Retreives directories and files used by Mycroft"""

    def __init__(self, base_path):
        self.base_path = base_path
        self.lang = 'en-us'

    @property
    def mod_path(self):
        return join(self.base_path, 'mycroft')

    @property
    def padatious_exe(self):
        """The locally compiled Padatious executable"""
        return join(self.base_path, 'padatious', 'build', 'src', 'padatious-mycroft')

    @property
    def skills_dir(self):
        return join(self.mod_path, 'skills')

    def skill_dir(self, skill_name):
        return join(self.mod_path, 'skills', to_snake(skill_name))

    def vocab_dir(self, skill_name):
        return join(self.skill_dir(skill_name), 'vocab', self.lang)

    def intent_dir(self, skill_name):
        return self.vocab_dir(skill_name)

    def dialog_dir(self, skill_name):
        return self.vocab_dir(skill_name)
