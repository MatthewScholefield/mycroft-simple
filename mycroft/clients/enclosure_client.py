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
from alsaaudio import Mixer
from os.path import join

from mycroft import main_thread
from mycroft.clients.mycroft_client import MycroftClient
from mycroft.util import logger
from mycroft.util.audio import play_wav


class EnclosureClient(MycroftClient):
    """Interact with Mycroft via the Mark 1 Enclosure"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        volume = self.global_config['volume']
        self.min = volume['min']
        self.max = volume['max']
        self.steps = volume['steps']
        self.change_volume_wav = join(self.path_manager.sounds_dir, 'change_volume.wav')

    def _change_volume(self, change):
        level = self.steps * (Mixer().getvolume()[0] - self.min) / (self.max - self.min)
        level += change
        level = min(max(level, 0), self.steps)
        Mixer().setvolume(round(100 * level / self.steps))
        self.format_manager.faceplate_command('eyes.volume=' + str(round(level)))
        play_wav(self.change_volume_wav)

    def run(self):
        while not main_thread.exit_event.is_set():
            line = self.format_manager.faceplate_readline()
            if 'volume.up' in line:
                self._change_volume(+1)
            elif 'volume.down' in line:
                self._change_volume(-1)
            elif len(line.strip()) > 0:
                logger.warning('Could not handle message: ' + line)

    def on_response(self, format_manager):
        pass
