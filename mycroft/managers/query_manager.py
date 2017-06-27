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
from threading import Thread


class QueryManager:
    """Launches queries in separate threads"""

    def __init__(self, intent_manager, format_manager):
        self.intent_manager = intent_manager
        self.format_manager = format_manager
        self.threads = []
        self.on_response_callbacks = []

    def _run_query(self, query):
        """Function to run query in a separate thread"""
        self.send_results(*self.intent_manager.calc_results(query))

    def send_results(self, name, results, actions):
        """Generates data in all the formats and gives that formatted data to each callback"""

        for i in actions:
            self.format_manager.generate(i, {})
            for i in self.on_response_callbacks:
                i(self.format_manager)

        if results is None:
            for i in self.on_response_callbacks:
                i(None)
        else:
            self.format_manager.generate(name, results)
            for i in self.on_response_callbacks:
                i(self.format_manager)

    def send_query(self, query):
        """Starts calculating a query in a new thread"""
        t = Thread(target=self._run_query, args=(query,))
        t.start()
        self.threads.append(t)

    def on_response(self, callback):
        """Assign a callback to be run whenever a new response comes in"""
        self.on_response_callbacks.append(callback)
