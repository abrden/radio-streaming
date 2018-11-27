import sys
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(threadName)s: %(message)s")

from .receiver import Receiver

COUNTRY_INDEX = 1
FREQUENCY_INDEX = 2


def main(args):
    r = Receiver(args[COUNTRY_INDEX], args[FREQUENCY_INDEX])
    r.start()


if __name__ == "__main__":
    main(sys.argv)
