from subprocess import Popen, PIPE

from mycroft.configuration import ConfigurationManager


def play_wav(file_name):
    cmd = ConfigurationManager.get().get('play_wav_cmdline').replace('%1', file_name)
    return Popen(cmd.split(), stdout=PIPE, stderr=PIPE)


def play_mp3(file_name):
    cmd = ConfigurationManager.get().get('play_mp3_cmdline').replace('%1', file_name)
    return Popen(cmd.split(), stdout=PIPE, stderr=PIPE)


def play_audio(file_name):
    ext = file_name.split('.')[-1]
    if ext == 'wav':
        return play_wav(file_name)
    elif ext == 'mp3':
        return play_mp3(file_name)
    else:
        raise ValueError('Unknown Extension: ' + ext)
