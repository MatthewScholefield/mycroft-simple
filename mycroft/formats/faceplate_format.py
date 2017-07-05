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

from mycroft.formats.mycroft_format import MycroftFormat
from mycroft.util import logger


class FaceplateFormat(MycroftFormat):
    """Format data into sentences"""

    def __init__(self, path_manager):
        super().__init__('.faceplate', path_manager)
        self.serial = serial.serial_for_url(url=self.config['port'],
                                            baudrate=self.config['rate'],
                                            timeout=self.config['timeout'])

    def clear(self):
        pass

    def command(self, message):
        logger.debug('Sending message: ' + message)
        self.serial.write((message + '\n').encode())

    def generate_format(self, file, data):
        for line in file.readlines():
            for key, val in data.items():
                line = line.replace('{' + key + '}', val)
            line = line.strip()
            if len(line) != 0 and '{' not in line and '}' not in line:
                self.command(line)
