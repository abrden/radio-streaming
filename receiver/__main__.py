import sys
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(threadName)s: %(message)s")

from .receiver import Receiver

ORIGIN_COUNTRY_INDEX = 1
COUNTRY_INDEX = 2
FREQUENCY_INDEX = 3


def main(args):
    r = Receiver(args[ORIGIN_COUNTRY_INDEX], args[COUNTRY_INDEX], args[FREQUENCY_INDEX])
    r.start()


if __name__ == "__main__":
    main(sys.argv)
