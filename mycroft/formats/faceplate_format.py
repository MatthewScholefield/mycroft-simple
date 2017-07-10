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
import serial
from threading import Thread

from queue import Queue

from mycroft.formats.mycroft_format import MycroftFormat
from mycroft.util import logger
from time import sleep, time as get_time


VISEMES = {
    # /A group
    'v': '5',
    'f': '5',
    # /B group
    'uh': '2',
    'w': '2',
    'uw': '2',
    'er': '2',
    'r': '2',
    'ow': '2',
    # /C group
    'b': '4',
    'p': '4',
    'm': '4',
    # /D group
    'aw': '1',
    # /E group
    'th': '3',
    'dh': '3',
    # /F group
    'zh': '3',
    'ch': '3',
    'sh': '3',
    'jh': '3',
    # /G group
    'oy': '6',
    'ao': '6',
    # /Hgroup
    'z': '3',
    's': '3',
    # /I group
    'ae': '0',
    'eh': '0',
    'ey': '0',
    'ah': '0',
    'ih': '0',
    'y': '0',
    'iy': '0',
    'aa': '0',
    'ay': '0',
    'ax': '0',
    'hh': '0',
    # /J group
    'n': '3',
    't': '3',
    'd': '3',
    'l': '3',
    # /K group
    'g': '3',
    'ng': '3',
    'k': '3',
    # blank mouth
    'pau': '4',
}


class FaceplateFormat(MycroftFormat):
    """Format data into sentences"""

    def __init__(self, path_manager):
        super().__init__('.faceplate', path_manager)
        enc_cfg = self.global_config['enclosure']
        self.serial = serial.serial_for_url(url=enc_cfg['port'], baudrate=enc_cfg['rate'], timeout=enc_cfg['timeout'])
        self.queue = Queue()

    def _reset(self):
        self.command('mouth.reset')
        self.command('eyes.reset')
        self.command('eyes.color=2068479')

    def visemes(self, dur_str):
        begin_time = get_time()
        for dur_cmd in dur_str.split(' '):
            parts = dur_cmd.split(':')
            if len(parts) != 2:
                continue

            phoneme = parts[0]
            desired_delta = float(parts[1])

            self.command('mouth.viseme=' + VISEMES.get(phoneme, 4))

            cur_delta = get_time() - begin_time
            sleep_time = desired_delta - cur_delta
            if sleep_time > 0:
                sleep(sleep_time)

    def run(self):
        while True:
            command = self.queue.get()
            logger.debug('Sending message: ' + command)
            self.serial.write((command + '\n').encode())
            self.queue.task_done()

    def command(self, message):
        self.queue.put(message)

    def readline(self):
        return self.serial.readline().decode()

    def _generate_format(self, file, data):
        for line in file.readlines():
            for key, val in data.items():
                line = line.replace('{' + key + '}', val)
            line = line.strip()
            if len(line) != 0 and '{' not in line and '}' not in line:
                self.command(line)
