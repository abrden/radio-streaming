import logging
import pyaudio

from .middleware import ReceiverMiddleware


class Receiver:
    def __init__(self, country, freq):
        self.logger = logging.getLogger("Receiver")
        self.logger.debug("Start with country: %s, frequency: %s", country, freq)

        self.country = country
        self.freq = freq
        self.logger.debug("Starting middleware")
        self.mw = ReceiverMiddleware(country, freq)

        self.logger.debug("Setting up audio stream")
        self.p = pyaudio.PyAudio()
        self.logger.debug("Receiving wave info")
        sampwidth = self.mw.receive_int()
        channels = self.mw.receive_int()
        rate = self.mw.receive_int()
        self.logger.debug("Creating stream")
        self.stream = self.p.open(format=self.p.get_format_from_width(sampwidth),
                                  channels=channels,
                                  rate=rate,
                                  output=True)

    def start(self):
        self.logger.debug("Receiving data from transmitter")
        data = self.mw.receive()

        while data != b"END":
            self.logger.debug("Received data of len: %d. Writing data to stream", len(data))
            self.stream.write(data)
            self.logger.debug("Receiving data from transmitter")
            data = self.mw.receive()

        self.logger.debug("Closing connection")
        self.mw.close()

        self.logger.debug("Closing audio stream")
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

