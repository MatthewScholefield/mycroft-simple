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
from threading import Event

from mycroft import mycroft_thread
from mycroft.clients.mycroft_client import MycroftClient


class TextClient(MycroftClient):
    """Interact with Mycroft via a terminal"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_event = Event()

    def run(self):
        while not mycroft_thread.exit_event.is_set():
            query = input("Input: ")
            self.response_event.clear()
            self.send_query(query)
            self.response_event.wait()

    def on_response(self, format_manager):
        if format_manager is not None:
            dialog = format_manager.as_dialog
            if len(dialog) > 0:
                print("    " + dialog)
                print()
        self.response_event.set()
