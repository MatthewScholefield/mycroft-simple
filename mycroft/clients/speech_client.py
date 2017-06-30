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
from os.path import join, abspath, dirname
from threading import Event

from speech_recognition import UnknownValueError

from mycroft import main_thread
from mycroft.clients.mycroft_client import MycroftClient
from mycroft.clients.speech.recognizers.pocketsphinx_recognizer import PocketsphinxListener
from mycroft.clients.speech.stt import STT
from mycroft.clients.speech.tts.mimic_tts import MimicTTS
from mycroft.configuration import ConfigurationManager
from mycroft.util import logger
from mycroft.util.audio import play_audio


class SpeechClient(MycroftClient):
    """Interact with Mycroft via a terminal"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exit = False
        self.response_event = Event()
        self.global_config = ConfigurationManager.get()
        self.listener = self.create_listener(self.path_manager)
        self.stt = STT()
        self.tts = MimicTTS(self.path_manager)
        root = abspath(dirname(__file__))
        self.start_listening_file = join(root, 'speech', 'sounds', self.global_config['sounds']['start_listening'])
        self.stop_listening_file = join(root, 'speech', 'sounds', self.global_config['sounds']['stop_listening'])

    def create_listener(self, path_manager):
        t = self.global_config['listener']['type']
        if t == 'PocketsphinxListener':
            return PocketsphinxListener(path_manager, self.global_config)
        else:
            raise ValueError

    def run(self):
        try:
            while not main_thread.exit_event.is_set():
                logger.debug('Waiting for wake word...')
                self.listener.wait_for_wake_word()
                logger.debug('Recording...')
                play_audio(self.start_listening_file)
                recording = self.listener.record_phrase()
                play_audio(self.stop_listening_file)
                logger.debug('Done recording.')
                try:
                    utterance = self.stt.execute(recording)
                    logger.debug('Utterance: ' + utterance)
                except UnknownValueError:
                    utterance = ''

                self.send_query(utterance)
                self.response_event.wait()
        except SystemExit:
            pass

    def on_response(self, format_manager):
        if format_manager is not None:
            dialog = format_manager.as_dialog
            if len(dialog) > 0:
                self.tts.speak(dialog)
        self.response_event.set()

    def on_exit(self):
        self.exit = True
        self.listener.on_exit()