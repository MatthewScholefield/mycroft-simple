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
from abc import ABCMeta, abstractmethod

from os.path import isfile, join

from mycroft.configuration import ConfigurationManager


class MycroftFormat(metaclass=ABCMeta):
    """
    Base class to provide an interface for different types of \"formats\"

    Formats are modes to display key-value data.
    For instance, the DialogFormat puts data into sentences
    The EnclosureFormat could put data into visual faceplate animations
    """

    def __init__(self, extension, path_manager):
        self._extension = extension
        self.path_manager = path_manager
        self.global_config = ConfigurationManager.get()
        self.config = self.global_config.get(self.__class__.__name__, {})

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def generate_format(self, file, data):
        pass

    def generate(self, name, data):
        """
        Translate the data into different formats
        Depending on the format, this can be accessed different ways
        Args:
            name (IntentName): full intent name
            data (dict): dict containing all data from the skill
        """
        self.clear()
        vocab_dir = self.path_manager.vocab_dir(name.skill)
        file_name = join(vocab_dir, name.intent + self._extension)
        if not isfile(file_name):
            return
        with open(file_name, 'r') as file:
            self.generate_format(file, data)
