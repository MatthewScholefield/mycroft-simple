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
import re
from genericpath import isfile
from os.path import join, dirname, expanduser

import yaml

from mycroft.util import to_snake

DEFAULT_CONFIG = join(dirname(__file__), 'data', 'mycroft.conf')
SYSTEM_CONFIG = '/etc/mycroft/mycroft.conf'
USER_CONFIG = join(expanduser('~'), '.mycroft/mycroft.conf')

REMOTE_CONFIG = 'mycroft.ai'
REMOTE_CACHE = '/opt/mycroft/web_config_cache.yaml'
IGNORED_SETTINGS = ["uuid", "@type", "active", "user", "device"]

load_order = [DEFAULT_CONFIG, REMOTE_CACHE, SYSTEM_CONFIG, USER_CONFIG]


class ConfigurationManager:
    __config = {}

    @classmethod
    def init(cls):
        cls.load_local()

    @classmethod
    def load_remote(cls):
        from mycroft.api import DeviceApi
        api = DeviceApi()
        setting = api.get_settings()
        cls.__store_cache(setting)
        cls.load_local()

    @classmethod
    def load_local(cls):
        cls.__config = {}

        def add_config(file_name):
            if isfile(file_name):
                with open(file_name) as f:
                    cls.__config.update(yaml.safe_load('\n'.join(f.readlines())))

        for i in load_order:
            add_config(i)

    @classmethod
    def get(cls):
        return cls.__config

    @staticmethod
    def load_skill_config(conf_file):
        if isfile(conf_file):
            with open(conf_file, 'r') as f:
                return yaml.safe_load(f)
        return {}

    @classmethod
    def __conv(cls, out, inp):
        """
        Converts remote config style to local config
        (Removes server specific entries)
        """
        for k, v in inp.items():
            if k not in IGNORED_SETTINGS:
                # Translate the CamelCase values stored remotely into the
                # Python-style names used within mycroft-core.
                key = to_snake(re.sub(r"Setting(s)?", "", k))
                if isinstance(v, dict):
                    out[key] = out.get(key, {})
                    cls.__conv(out[key], v)
                elif isinstance(v, list):
                    if key not in out:
                        out[key] = {}
                    cls.__conv_list(out[key], v)
                else:
                    out[key] = v

    @classmethod
    def __conv_list(cls, out, inp):
        for v in inp:
            mod = v["@type"]
            if v.get("active"):
                out["module"] = mod
            out[mod] = out.get(mod, {})
            cls.__conv(out[mod], v)

    @classmethod
    def __store_cache(cls, setting):
        """Save last version of remote config for future use"""
        config = {}
        cls.__conv(config, setting)
        with open(REMOTE_CACHE, 'w') as f:
            yaml.dump(config, f)
