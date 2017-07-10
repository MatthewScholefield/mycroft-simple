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


class MycroftClient(metaclass=ABCMeta):
    """
    Provides common behavior like sending and receiving queries
    Examples clients include the voice client and text client
    """

    def __init__(self, path_manager, query_manager, format_manager):
        self.path_manager = path_manager
        self.format_manager = format_manager
        self._query_manager = query_manager
        self._query_manager.on_response(self.on_response)

    def send_query(self, query):
        """Ask a question and trigger on_response when an answer is found"""
        self._query_manager.send_query(query)

    @abstractmethod
    def run(self):
        """Executes the main thread for the client"""
        pass

    @abstractmethod
    def on_response(self, format_manager):
        """Called after send_query. Use format_manager to get outputted response"""
        pass

    def on_exit(self):
        pass
