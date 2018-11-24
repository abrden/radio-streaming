import logging
import wave

from .middleware import TransmitterMiddleware

CHUNK = 1024


class Transmitter:
    def __init__(self, country, freq, audio_file_path):
        self.logger = logging.getLogger("Transmitter")
        self.logger.debug("Start with country: %s, frequency: %s, audio: %s", country, freq, audio_file_path)

        self.country = country
        self.freq = freq
        self.audio_file_path = audio_file_path
        self.logger.debug("Starting middleware")
        self.mw = TransmitterMiddleware(country, freq)

    def start(self):
        self.logger.debug("Opening audio file")
        wf = wave.open(self.audio_file_path, 'rb')

        self.logger.debug("Sending wave info")
        sampwidth = wf.getsampwidth()
        self.mw.send_int(sampwidth)
        channels = wf.getnchannels()
        self.mw.send_int(channels)
        rate = wf.getframerate()
        self.mw.send_int(rate)

        self.logger.debug("Reading CHUNK from audio file")
        data = wf.readframes(CHUNK)

        while data != '':
            self.logger.debug("Read data of len: %d", len(data))
            self.mw.send(data)
            self.logger.debug("Reading CHUNK from audio file")
            data = wf.readframes(CHUNK)

        self.logger.debug("Closing audio file")
        wf.close()
        self.logger.debug("Closing connection")
        self.mw.close()


