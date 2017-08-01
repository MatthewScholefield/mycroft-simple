#!/usr/bin/env python3

from setuptools import setup

setup(
    name='mycroft_simple',
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
        'PyYAML>=3.12',
        'requests>=2.13.0',
        'pocketsphinx>=0.1.3',
        'SpeechRecognition>=3.7.1',
        'PyAudio>=0.2.11',
        'pyserial==3.3',
        'pyalsaaudio==0.8.4',
        'tornado==4.5.1',
        'websocket-client==0.44.0',
        'padatious',

        # Extra deps required for some installations
        'urllib3>=1.21.1,<1.22',
        'certifi>=2017.4.17',
        'chardet>=3.0.2,<3.1.0',
        'idna>=2.5,<2.6',

        # Skill dependencies
        'multi-key-dict>=2.0.3',
        'pyowm==2.6.1',
        'ddg3==0.6.5',
        'parsedatetime==2.4',
        'geopy==1.11.0',
        'pytz==2017.2',
        'pyjokes==0.5.0',
        'cleverwrap==0.2.3.6',
        'pydora==1.9.0',
        'psutil==5.2.2'
    ],
    entry_points={
        'console_scripts': [
            'mycroft_simple = mycroft.main:main'
        ]
    },
    include_package_data=True,
    zip_safe=False
)
