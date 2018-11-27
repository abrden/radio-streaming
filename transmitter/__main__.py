import sys
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(threadName)s: %(message)s")

from .transmitter import Transmitter

COUNTRY_INDEX = 1
FREQUENCY_INDEX = 2
AUDIO_FILE_INDEX = 3


def main(args):
    t = Transmitter(args[COUNTRY_INDEX], args[FREQUENCY_INDEX], args[AUDIO_FILE_INDEX])
    t.start()


if __name__ == "__main__":
    main(sys.argv)
