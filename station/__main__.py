import sys
import os
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(threadName)s: %(message)s")

from .station import Station

def main(args):
    s = Station(os.environ['COUNTRY'], int(os.environ['STATION_NUM']), int(os.environ['STATIONS_TOTAL']))
    try:
        s.start()
    except KeyboardInterrupt:
        s.close()


if __name__ == "__main__":
    main(sys.argv)
