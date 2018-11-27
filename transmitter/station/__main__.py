import sys
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(threadName)s: %(message)s")

from .station import Station

COUNTRY_INDEX = 1


def main(args):
    s = Station(args[COUNTRY_INDEX])
    s.start()


if __name__ == "__main__":
    main(sys.argv)
