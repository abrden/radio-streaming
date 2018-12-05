import os
import sys
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(threadName)s: %(message)s")

from .receiver import Receiver


def main(args):
    r = Receiver(os.environ['COUNTRY'], os.environ['FREQUENCY'], int(os.environ['STATIONS_TOTAL']))
    r.start()


if __name__ == "__main__":
    main(sys.argv)
