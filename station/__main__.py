import sys
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(threadName)s: %(message)s")

from .station import Station

def main(args):
    s = Station()


if __name__ == "__main__":
    main(sys.argv)