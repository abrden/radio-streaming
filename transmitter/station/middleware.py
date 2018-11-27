import zmq


class StationMiddleware:
    def __init__(self, country):
        # TODO Do things with country
        context = zmq.Context()

        # Socket facing producers
        self.transmitters = context.socket(zmq.XPUB)
        self.transmitters.bind("tcp://*:5000")

        # Socket facing consumers
        self.receivers = context.socket(zmq.XSUB)
        self.receivers.bind("tcp://*:5001")

        zmq.proxy(self.transmitters, self.receivers)

    def close(self):
        self.transmitters.close()
        self.receivers.close()
        # TODO Terminate context
