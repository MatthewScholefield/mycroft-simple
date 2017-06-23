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


class MycroftFormat(metaclass=ABCMeta):
    """
    Base class to provide an interface for different types of \"formats\"

    Formats are modes to display key-value data.
    For instance, the DialogFormat puts data into sentences
    The EnclosureFormat could put data into visual faceplate animations
    """

    def __init__(self, path_manager):
        self.path_manager = path_manager

    @abstractmethod
    def generate(self, name, results):
        """
        Internally format the data from the results
        Depending on the format, this can be accessed different ways

        :param name: namespaced intent name
        :param results: dict containing all data from the skill
        :returns: nothing
        """
        pass
