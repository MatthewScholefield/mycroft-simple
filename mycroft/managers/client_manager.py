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


class ClientManager:
    """Holds all clients to start and stop them"""

    def __init__(self, client_classes, *args, **kwargs):

        self.clients = [i(*args, **kwargs) for i in client_classes]
        self.client_threads = [Thread(target=client.run) for client in self.clients]

    def start(self):
        """Starts all clients in different threads (non blocking)"""
        for i in self.client_threads:
            i.start()

    def quit(self):
        """Sends a signal to all clients to quit. Does not wait for clients to exit (non blocking)"""
        for i in self.clients:
            i.quit()
