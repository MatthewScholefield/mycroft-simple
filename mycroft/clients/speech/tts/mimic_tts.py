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
from os import chdir, getcwd, mkdir
from os.path import isdir, isfile, join
from subprocess import call

from mycroft.clients.speech.tts.mycroft_tts import MycroftTTS


class MimicTTS(MycroftTTS):
    GIT_URL = 'https://github.com/MycroftAI/mimic.git'
    VERSION = '1.2.0.2'

    SCRIPT_URL = 'https://github.com/MatthewScholefield/mycroft-simple.git'
    SCRIPT_BRANCH = 'mimic-script'

    def __init__(self, path_manager):
        super().__init__(path_manager)

        if not isfile(self.path_manager.mimic_exe):
            self._build()

    def _build(self):
        mimic_dir = self.path_manager.mimic_dir
        if not isdir(mimic_dir):
            mkdir(mimic_dir)
        cur_path = getcwd()
        try:
            chdir(mimic_dir)

            if not isdir('.git'):
                pass

            if not isdir('scripts'):
                call(['git', 'clone', '-b', self.SCRIPT_BRANCH, '--single-branch', self.SCRIPT_URL, 'scripts'])

            call(['sh', join('scripts', 'build-mimic.sh')])
        finally:
            chdir(cur_path)

    def speak(self, text):
        call([self.path_manager.mimic_exe, '-t', text])
