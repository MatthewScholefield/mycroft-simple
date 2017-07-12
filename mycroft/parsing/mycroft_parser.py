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
import sys
from abc import ABCMeta, abstractmethod

from enum import Enum, unique

@unique
class TimeType(Enum):
    SEC = 1
    MIN = SEC * 60
    HR = MIN * 60
    DAY = HR * 24

    def to_sec(self, amount):
        return amount * self.value

    def from_sec(self, num_sec):
        return num_sec / self.value


class MycroftParser(metaclass=ABCMeta):
    """Helper class to parse common parameters like duration out of strings"""
    def __init__(self):
        pass

    @abstractmethod
    def format_quantities(self, quantities):
        """
        Arranges list of tuples of (ttype, amount) into language
        [(MIN, 12), (SEC, 3)] -> '12 minutes and three seconds'
        Args:
            quantities(list<tuple<TimeType, int>>):

        Returns:
            quantities(str): quantities in natural language
        """
        pass

    @abstractmethod
    def duration(self, str):
        """
        Returns duration in natural language string in seconds
        Raises: ValueError, if nothing found
        """
        pass

    def duration_to_str(self, dur):
        """
        Converts duration in seconds to appropriate time format in natural langauge
        70 -> '1 minute and 10 seconds'
        """
        quantities = []
        left_amount = dur
        for ttype in reversed(list(TimeType)):
            amount = ttype.from_sec(left_amount)
            int_amount = int(amount + 0.000000001)
            left_amount = ttype.to_sec(amount - int_amount)
            if int_amount > 0:
                quantities.append((ttype, int_amount))
        return self.format_quantities(quantities)
