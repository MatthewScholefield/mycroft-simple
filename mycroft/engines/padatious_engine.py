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
import json
import os
import subprocess
from os.path import isfile
from subprocess import Popen
from threading import Event, Thread

from websocket_server import WebsocketServer

from mycroft.engines.intent_engine import IntentEngine, IntentMatch
from mycroft.skill import IntentName
from mycroft.util import logger
from mycroft.util.git_repo import GitRepo


class PadatiousEngine(IntentEngine):
    """Interface for Padatious intent engine"""
    HOST = '127.0.0.1'
    PORT = 8014

    def __init__(self, path_manager):
        """Opens Padatious process and waits for it to connect"""
        super().__init__(path_manager)

        self.git_repo = GitRepo(dir=self.path_manager.padatious_dir,
                                url='https://github.com/MatthewScholefield/padatious-mycroft.git',
                                branch='feature/mycroft-simple',
                                update_freq=1)
        if self.git_repo.try_pull() or not isfile(self.path_manager.padatious_exe):
            self.git_repo.run_inside('sh build.sh update')

        self.new_message = None
        self.new_message_event = Event()

        self.server, connected_event = self._create_server()
        self._start_server()
        self.process = self._create_process()
        if not connected_event.wait(4):
            raise TimeoutError('Could not connect websocket to Padatious')

    def _create_server(self):
        """Creates a websocket server to communicate with the padatious process"""
        server = WebsocketServer(host=PadatiousEngine.HOST, port=PadatiousEngine.PORT)

        def on_message(server, client, message):
            self.new_message = message
            self.new_message_event.set()

        connected_event = Event()

        def on_connected(server, client):
            connected_event.set()

        server.set_fn_message_received(on_message)
        server.set_fn_new_client(on_connected)
        return server, connected_event

    def _create_process(self):
        """Opens the padatious process silently"""
        return Popen([self.path_manager.padatious_exe], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def _start_server(self):
        """Creates server in new thread as daemon (will run forever until program terminates)"""
        Thread(target=self.server.run_forever, daemon=True).start()

    def _send_request(self, request, parameters={}):
        """Ask the padatious process to do something"""
        parameters['request'] = request
        self.server.send_message_to_all(json.dumps(parameters))

    def try_register_intent(self, skill_name, intent_name):
        if not isinstance(intent_name, str):
            return None
        intent_dir = self.path_manager.intent_dir(skill_name)
        file_name = os.path.join(intent_dir, intent_name + '.intent')
        if not os.path.isfile(file_name):
            return None

        name = IntentName(skill_name, intent_name)
        self._send_request('register_intent', {'name': str(name), 'file_name': file_name})
        return name

    def on_intents_loaded(self):
        self._send_request('train')
        print('Training...')
        logger.debug('Training Padatious...')
        if not self.new_message_event.wait(40):
            logger.debug('Taking longer than expected to train...')
            if not self.new_message_event.wait(200):
                raise TimeoutError('Taking too long to train intents')
        logger.debug('Training complete!')
        print('Training complete!')

    def calc_intents(self, query):
        self.new_message_event.clear()
        self._send_request('calc_intents', {'query': query})
        if not self.new_message_event.wait(4):
            raise TimeoutError('When asking to calculate intents from Padatious')
        match_dicts = json.loads(self.new_message)['matches']
        return [IntentMatch.from_dict(i) for i in match_dicts]
