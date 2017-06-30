#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='mycroft_simple',
      version='0.1',
      description='A redesigned Mycroft implementation',
      url='http://github.com/MatthewScholefield/mycroft-simple',
      author='Mycroft AI Inc.',
      author_email='support@mycroft.ai',
      license='Apache-2.0',
      packages=[
          'mycroft',
          'mycroft.clients',
          'mycroft.clients.speech',
          'mycroft.clients.speech.recognizers',
          'mycroft.clients.speech.tts',
          'mycroft.engines',
          'mycroft.formats',
          'mycroft.managers'
      ],
      install_requires=[
          'websocket_server>=0.4',
          'PyYAML>=3.12',
          'requests>=2.18.1',
          'pocketsphinx>=0.1.3',
          'SpeechRecognition>=3.7.1',
          'PyAudio>=0.2.11'
      ],
      entry_points={
          'console_scripts': [
              'mycroft_simple = mycroft.main:main'
          ]
      },
      include_package_data=True,
      zip_safe=False)
