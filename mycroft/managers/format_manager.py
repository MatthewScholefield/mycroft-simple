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
from mycroft.formats.dialog_format import DialogFormat
from mycroft.formats.faceplate_format import FaceplateFormat
from mycroft.util import logger


class FormatManager:
    """Holds all formats and provides an interface to access them"""

    def __init__(self, path_manager):
        self.formats = []

        def create(cls):
            try:
                instance = cls(path_manager)
                self.formats.append(instance)
                return instance
            except Exception as e:
                logger.print_e(e, self.__class__.__name__)
                return None

        self.dialog_format = create(DialogFormat)
        self.faceplate_format = create(FaceplateFormat)

    def generate(self, name, results):
        for i in self.formats:
            i.generate(name, results)

    @property
    def as_dialog(self):
        """Get data as a sentence"""
        return '' if self.dialog_format is None else self.dialog_format.output

    def faceplate_command(self, message):
        if self.faceplate_format is not None:
            self.faceplate_format.command(message)

